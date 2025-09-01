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

    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_PERSIST_DIR))
    collection_name = "southoftethys"
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
            ids.append(f"{f.stem}_{ci}")
            docs.append(chunk)
            metadatas.append({"source": str(f), "chunk_index": ci})

    if docs:
        collection.add(ids=ids, documents=docs, metadatas=metadatas)
        client.persist()
        print(f"Indexed {len(docs)} chunks into Chroma at {CHROMA_PERSIST_DIR}")
    else:
        print("No documents found to index.")


if __name__ == "__main__":
    main()
