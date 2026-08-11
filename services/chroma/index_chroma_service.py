"""
Dedicated Chroma indexer service.

Indexes canonical lore from database/**/*.json (and optional snippets/inbox).
Persists to CHROMA_PERSIST_DIR or Chroma Cloud when API key is set.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except Exception:
    raise SystemExit(
        "Required packages missing. Install chromadb and sentence-transformers."
    )

_VALIDATE = False
try:
    from services.chroma.schemas.validate_metadata import validate as validate_metadata

    _VALIDATE = True
except Exception:
    _VALIDATE = False

REPO_DIR = os.environ.get("REPO_DIR", "/app/repo")
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "/data/chroma")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = "southoftethys"

# Canon folders under database/
DB_FOLDERS = [
    "characters",
    "events",
    "fauna",
    "flora",
    "settlements",
    "regions",
    "artifacts",
    "factions",
    "mythology",
]


def gather_files(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    db = repo_root / "database"
    if db.exists():
        for folder in DB_FOLDERS:
            d = db / folder
            if d.exists():
                candidates.extend(sorted(d.glob("*.json")))
        index = db / "index.json"
        if index.exists():
            candidates.append(index)
    # Optional inbox for raw extraction snippets
    inbox = repo_root / "snippets" / "inbox"
    if inbox.exists():
        candidates.extend(sorted(inbox.rglob("*.md")))
        candidates.extend(sorted(inbox.rglob("*.txt")))
        candidates.extend(sorted(inbox.rglob("*.json")))
    return candidates


def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    words = text.split()
    if not words:
        return [text] if text.strip() else []
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


def headline(payload: dict[str, Any]) -> str:
    """One prose sentence naming the entity.

    The flattened `key: value` lines below embed poorly against natural questions
    like "Who is Kavik Stoneheart?" — field names dominate and the entity's own
    name appears once. Leading with a sentence that carries the name, aliases and
    epithets gives the embedder something question-shaped to match.
    """
    name = payload.get("name") or payload.get("title") or payload.get("id")
    if not name:
        return ""

    naming = [str(name)]
    aliases = payload.get("aliases")
    if aliases:
        naming.append("also known as " + ", ".join(str(a) for a in aliases))
    epithets = payload.get("epithets")
    if epithets:
        naming.append("called " + ", ".join(str(e) for e in epithets))
    sentence = "; ".join(naming)

    # e.g. "a harappan human character of the civilization_dawn epoch"
    descriptors = [
        str(payload[key])
        for key in ("culture", "species", "type")
        if payload.get(key)
    ]
    if descriptors:
        sentence += " is a " + " ".join(descriptors)
    epoch = payload.get("epoch")
    if epoch:
        sentence += f" of the {epoch} epoch"

    return sentence + "."


def entity_document(payload: dict[str, Any]) -> str:
    """Flatten entity JSON into searchable prose."""
    parts: list[str] = []
    lead = headline(payload)
    if lead:
        parts.append(lead)
    for key in (
        "id",
        "type",
        "name",
        "title",
        "epithets",
        "aliases",
        "culture",
        "species",
        "epoch",
        "status",
        "roles",
        "summary",
        "notes",
        "diet",
        "habitats",
        "behaviour",
        "uses",
        "power",
        "risk",
        "material",
        # Species fields. `journal_prompt` is the richest prose on a species -- the
        # sentence the player actually reads -- and was absent here, so 300-odd entities
        # were indexed on their reference notes alone. `biomes` and `crosses_at` say where
        # a species lives and how it gets here, which is most of what anyone asks about
        # one; without them "which creatures live in the Naraka rifts?" could not be
        # answered from an index that already contained all six of them.
        "scientific",
        "journal_prompt",
        "region",
        "biomes",
        "placement",
        "rarity",
        "mood",
        "crosses_at",
        "placement_note",
    ):
        val = payload.get(key)
        if val is None or val == "" or val == []:
            continue
        if isinstance(val, list):
            parts.append(f"{key}: {', '.join(str(v) for v in val)}")
        else:
            parts.append(f"{key}: {val}")
    # relations / graph fields
    for key in (
        "relations",
        "participants",
        "predecessors",
        "successors",
        "outcomes",
        "causes",
        "related_characters",
        "events",
        "artifacts",
    ):
        val = payload.get(key)
        if not val:
            continue
        if isinstance(val, dict):
            parts.append(f"{key}: {json.dumps(val, ensure_ascii=False)}")
        elif isinstance(val, list):
            parts.append(f"{key}: {', '.join(str(v) for v in val)}")
        else:
            parts.append(f"{key}: {val}")
    return "\n".join(parts) if parts else json.dumps(payload, ensure_ascii=False)


def build_metadata(repo_root: Path, fpath: Path, payload: dict | None, chunk_index: int):
    # as_posix() so metadata is identical whether indexed on Windows or in Docker.
    rel = fpath.relative_to(repo_root).as_posix()
    meta: dict[str, Any] = {"source": rel, "chunk_index": chunk_index}
    if payload and isinstance(payload, dict):
        eid = payload.get("id") or fpath.stem
        meta["entity_id"] = eid
        meta["entity_type"] = payload.get("type") or fpath.parent.name.rstrip("s")
        if payload.get("name"):
            meta["name"] = payload["name"]
        if payload.get("title"):
            meta["title"] = payload["title"]
        if payload.get("epoch"):
            meta["epoch"] = payload["epoch"]
        if payload.get("culture"):
            meta["culture"] = payload["culture"]
        # Species facets, for filtering rather than matching. Chroma metadata values must
        # be scalars, so the biome list is joined -- enough to filter on with a substring
        # check, and the prose carries it properly for semantic matching.
        if payload.get("placement"):
            meta["placement"] = payload["placement"]
        if payload.get("rarity"):
            meta["rarity"] = payload["rarity"]
        if payload.get("region"):
            meta["region"] = payload["region"]
        if payload.get("biomes"):
            meta["biomes"] = ", ".join(str(b) for b in payload["biomes"])
    else:
        meta["entity_id"] = fpath.stem
    return meta


def get_client():
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    if cloud_key:
        tenant = os.environ.get("CHROMA_TENANT")
        database = os.environ.get("CHROMA_DATABASE")
        return chromadb.CloudClient(
            api_key=cloud_key, tenant=tenant, database=database
        )
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_embedding_function():
    """Shared with query-time code so index and search use the same vectors.

    Chroma's default embedder by preference. It is the same model as before --
    all-MiniLM-L6-v2, Apache-2.0, 384 dimensions -- but it runs on ONNX Runtime instead of
    torch. That is the difference between a service that needs 694MB of dependencies and one
    that needs about 80MB, which is the difference between paying to host this and not.

    Set EMBEDDING_BACKEND=sentence-transformers to use the torch path instead. Whatever this
    returns must be used for both indexing and querying: writing vectors with one embedder
    and reading with another silently ruins every result, which this repo has already done
    once.
    """
    if os.environ.get("EMBEDDING_BACKEND", "onnx").lower().startswith("sentence"):
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return embedding_functions.DefaultEmbeddingFunction()


def main():
    repo_root = Path(REPO_DIR)
    if not repo_root.exists():
        raise SystemExit(f"Repo directory not found: {REPO_DIR}")

    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME, embedding_function=get_embedding_function()
    )

    files = gather_files(repo_root)
    ids, docs, metadatas = [], [], []

    for f in files:
        raw = f.read_text(encoding="utf-8")
        payload = None
        if f.suffix == ".json":
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = None
            text = (
                entity_document(payload)
                if isinstance(payload, dict)
                else raw
            )
        else:
            text = raw

        chunks = chunk_text(text, chunk_size=200)
        for ci, chunk in enumerate(chunks):
            vid = f"{f.stem}_{ci}"
            meta = build_metadata(repo_root, f, payload if isinstance(payload, dict) else None, ci)

            if os.environ.get("INSERT_VALIDATE") and _VALIDATE:
                coll = meta.get("entity_type", "documents")
                if coll in {"character", "characters"}:
                    coll = "characters"
                elif coll in {"event", "events"}:
                    coll = "events"
                else:
                    coll = "documents"
                try:
                    validate_metadata(
                        coll, {"id": vid, "text": chunk, "metadata": meta}
                    )
                except Exception as e:
                    print(f"Validation failed for {vid}: {e}")
                    continue

            ids.append(vid)
            docs.append(chunk)
            metadatas.append(meta)

    if docs:
        collection.add(ids=ids, documents=docs, metadatas=metadatas)
        print(
            f"Indexed {len(docs)} chunks from {len(files)} files "
            f"into '{COLLECTION_NAME}'"
        )
    else:
        print("No documents found to index under database/.")


if __name__ == "__main__":
    main()
