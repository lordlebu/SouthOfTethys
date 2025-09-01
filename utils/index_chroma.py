"""
Index story files into a Chroma vector store.

This is a helper script to be run locally. It expects Chroma and sentence-transformers to be installed.
It reads story files from `timeline/`, `characters/`, and `snippets/inbox/` and creates a persistent Chroma index at
the directory specified by the `CHROMA_PERSIST_DIR` environment variable (default: `storage/chroma`).

Run locally:
    CHROMA_PERSIST_DIR=storage/chroma python utils/index_chroma.py

Note: This script is intentionally minimal and expects the user to adapt chunking and metadata to their needs.
"""
import os
from pathlib import Path
from typing import List

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except Exception as e:
    raise SystemExit("Required packages missing. Install chromadb and sentence-transformers.")

CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "storage/chroma")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def gather_text_files() -> List[Path]:
    base = Path.cwd()
    candidates = []
    for folder in [base / "timeline", base / "characters", base / "snippets" / "inbox"]:
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
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_PERSIST_DIR))
    collection_name = "southoftethys"
    try:
        collection = client.get_collection(collection_name)
        # clear existing for fresh index
        collection.delete()
        collection = client.create_collection(collection_name)
    except Exception:
        collection = client.create_collection(collection_name)

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    files = gather_text_files()
    ids, docs, metadatas = [], [], []
    idx = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        chunks = chunk_text(text, chunk_size=200)
        for ci, chunk in enumerate(chunks):
            ids.append(f"{f.stem}_{ci}")
            docs.append(chunk)
            metadatas.append({"source": str(f), "chunk_index": ci})
            idx += 1
    if docs:
        collection.add(ids=ids, documents=docs, metadatas=metadatas)
        client.persist()
        print(f"Indexed {len(docs)} chunks into Chroma at {CHROMA_PERSIST_DIR}")
    else:
        print("No documents found to index.")


if __name__ == "__main__":
    main()
