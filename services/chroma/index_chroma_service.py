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
    from sentence_transformers import SentenceTransformer
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


def entity_document(payload: dict[str, Any]) -> str:
    """Flatten entity JSON into searchable prose."""
    parts: list[str] = []
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
    rel = str(fpath.relative_to(repo_root))
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
        ), True
    client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=CHROMA_PERSIST_DIR,
        )
    )
    return client, False


def main():
    repo_root = Path(REPO_DIR)
    if not repo_root.exists():
        raise SystemExit(f"Repo directory not found: {REPO_DIR}")

    client, is_cloud = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    # Load embedder so model is warm (chromadb may also embed depending on config)
    SentenceTransformer(EMBEDDING_MODEL)

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
        if not is_cloud:
            try:
                client.persist()
            except Exception:
                pass
        print(
            f"Indexed {len(docs)} chunks from {len(files)} files "
            f"into '{COLLECTION_NAME}'"
        )
    else:
        print("No documents found to index under database/.")


if __name__ == "__main__":
    main()
