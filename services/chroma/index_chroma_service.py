"""
Dedicated Chroma indexer service

This script is intended to run inside the `services/chroma` container and will build/update a persistent
Chroma index at the path pointed to by `CHROMA_PERSIST_DIR` (default: `/data/chroma`).

It reads story files from the repository mounted into `/app/repo` and writes Chroma storage to `/data/chroma`.
"""
import os
from pathlib import Path
from typing import List

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except Exception:
    raise SystemExit("Required packages missing. Make sure to install requirements.txt")

_VALIDATE = False
try:
    from services.chroma.schemas.validate_metadata import validate as validate_metadata
    _VALIDATE = True
except Exception:
    # validator is optional; controlled by INSERT_VALIDATE env var at runtime
    _VALIDATE = False

# Service defaults
REPO_DIR = os.environ.get("REPO_DIR", "/app/repo")
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "/data/chroma")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def gather_text_files(repo_root: Path) -> List[Path]:
    candidates = []
    for folder in [repo_root / "timeline", repo_root / "characters", repo_root / "snippets" / "inbox"]:
        if folder.exists():
            for p in folder.rglob("*.json"):
                candidates.append(p)
            for p in folder.rglob("*.md"):
                candidates.append(p)
    return candidates


def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks


def main():
    repo_root = Path(REPO_DIR)
    if not repo_root.exists():
        raise SystemExit(f"Repo directory not found: {REPO_DIR}")

    # Support Chroma Cloud if API key provided, otherwise use local DuckDB+Parquet persistence
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    collection_name = "southoftethys"
    if cloud_key:
        # Use CloudClient for remote Chroma; tenant and database may be provider specific
        tenant = os.environ.get("CHROMA_TENANT")
        database = os.environ.get("CHROMA_DATABASE")
        client = chromadb.CloudClient(api_key=cloud_key, tenant=tenant, database=database)
        try:
            # recreate collection if exists
            client.delete_collection(collection_name)
        except Exception:
            pass
        collection = client.create_collection(collection_name)
    else:
        client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_PERSIST_DIR))
        try:
            # Recreate collection for fresh index
            client.delete_collection(collection_name)
        except Exception:
            pass
        collection = client.create_collection(collection_name)

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    files = gather_text_files(repo_root)
    ids, docs, metadatas = [], [], []
    for f in files:
        text = f.read_text(encoding="utf-8")
        chunks = chunk_text(text, chunk_size=200)
        for ci, chunk in enumerate(chunks):
            vid = f"{f.stem}_{ci}"
            ids.append(vid)
            docs.append(chunk)
            # build richer metadata depending on folder
            rel = str(f.relative_to(repo_root))
            meta = {"source": rel, "chunk_index": ci}
            if rel.startswith("timeline/"):
                # try to pull event_id/title/date from json if available
                try:
                    import json
                    payload = json.loads(text)
                    event_id = payload.get("id") or f.stem
                    meta.update({"event_id": event_id, "title": payload.get("title"), "date": payload.get("date")})
                except Exception:
                    meta.update({"event_id": f.stem})
            elif rel.startswith("characters/"):
                try:
                    import json
                    payload = json.loads(text)
                    char_id = payload.get("id") or f.stem
                    meta.update({"character_id": char_id, "name": payload.get("name") or payload.get("id")})
                except Exception:
                    meta.update({"character_id": f.stem, "name": f.stem})
            elif rel.startswith("snippets/"):
                meta.update({"snippet_id": f.stem})

            # optional validation before adding
            if os.environ.get("INSERT_VALIDATE") and _VALIDATE:
                coll = None
                if rel.startswith("timeline/"):
                    coll = "events"
                elif rel.startswith("characters/"):
                    coll = "characters"
                elif rel.startswith("snippets/"):
                    coll = "snippets"
                if coll:
                    try:
                        validate_metadata(coll, {"id": vid, "text": chunk, "metadata": meta})
                    except Exception as e:
                        print(f"Validation failed for {vid}: {e}")
                        continue

            metadatas.append(meta)

    if docs:
        collection.add(ids=ids, documents=docs, metadatas=metadatas)
        client.persist()
        print(f"Indexed {len(docs)} chunks into Chroma at {CHROMA_PERSIST_DIR}")
    else:
        print("No documents found to index.")


if __name__ == "__main__":
    main()
