#!/usr/bin/env python3
"""Query the canon Chroma index from the command line.

Smoke-checks retrieval without Streamlit or any language-model download.

Examples:
  python scripts/query_chroma.py "Who is Kavik Stoneheart?"
  python scripts/query_chroma.py "Mask of Tethys" --k 3
  python scripts/query_chroma.py "Tendua Crisis" --expect event_tendua_crisis
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except Exception:
    raise SystemExit(
        "chromadb is required. Install services/chroma/requirements.txt"
    )

REPO_ROOT = Path(__file__).resolve().parent.parent
COLLECTION_NAME = "southoftethys"


def get_collection(persist_dir: str, embedding_model: str):
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    if cloud_key:
        client = chromadb.CloudClient(
            api_key=cloud_key,
            tenant=os.environ.get("CHROMA_TENANT"),
            database=os.environ.get("CHROMA_DATABASE"),
        )
    else:
        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    return client.get_collection(COLLECTION_NAME, embedding_function=ef)


def main() -> int:
    p = argparse.ArgumentParser(description="Query the canon Chroma index")
    p.add_argument("query", help="Natural-language query")
    p.add_argument("--k", type=int, default=5, help="Number of results")
    p.add_argument(
        "--expect",
        help="Fail unless this entity_id appears in the results",
    )
    p.add_argument(
        "--persist-dir",
        default=os.environ.get(
            "CHROMA_PERSIST_DIR", str(REPO_ROOT / "storage" / "chroma")
        ),
    )
    p.add_argument(
        "--embedding-model",
        default=os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )
    p.add_argument("--show-text", action="store_true", help="Print chunk text")
    args = p.parse_args()

    try:
        collection = get_collection(args.persist_dir, args.embedding_model)
    except Exception as e:
        print(f"Could not open collection '{COLLECTION_NAME}': {e}")
        print(f"Build the index first (persist dir: {args.persist_dir}):")
        print("  python services/chroma/index_chroma_service.py")
        return 1

    results = collection.query(
        query_texts=[args.query],
        n_results=args.k,
        include=["metadatas", "documents", "distances"],
    )
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    if not documents:
        print(f"No results for: {args.query}")
        return 1

    print(f"Query: {args.query}")
    print(f"Collection: {COLLECTION_NAME} ({collection.count()} chunks)\n")

    entity_ids = []
    for rank, (doc, meta, dist) in enumerate(
        zip(documents, metadatas, distances), start=1
    ):
        meta = meta or {}
        entity_id = meta.get("entity_id", "—")
        entity_ids.append(entity_id)
        name = meta.get("name") or meta.get("title") or ""
        suffix = f" ({name})" if name else ""
        print(f"{rank}. {meta.get('source', 'unknown')}")
        print(f"   entity_id={entity_id}{suffix}  distance={dist:.4f}")
        if args.show_text:
            print(f"   {doc[:300]}")
    print()

    if args.expect:
        if args.expect in entity_ids:
            print(f"PASS: '{args.expect}' found in top {args.k}")
        else:
            print(f"FAIL: '{args.expect}' not in top {args.k}: {entity_ids}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
