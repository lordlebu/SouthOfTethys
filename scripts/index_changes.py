#!/usr/bin/env python3
"""Incremental indexer: upsert changed files into Chroma (local or cloud).

Prefer database/ paths. Also accepts snippets/inbox.

Examples:
  python scripts/index_changes.py --files database/characters/character_kavik.json
  python scripts/index_changes.py --git-range HEAD~1..HEAD
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# Reuse the full indexer's text/metadata builders so an incremental upsert
# produces byte-identical chunks to a full rebuild of the same file.
sys.path.insert(0, str(REPO_ROOT / "services" / "chroma"))
from index_chroma_service import (  # noqa: E402  (import follows sys.path setup)
    build_metadata,
    chunk_text,
    entity_document,
)

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except Exception:
    raise SystemExit(
        "chromadb is required. Install services/chroma/requirements.txt"
    )

try:
    import sentence_transformers  # noqa: F401  (backs the embedding function below)
except Exception:
    raise SystemExit("sentence-transformers is required")

_HAVE_VALIDATOR = False
try:
    from services.chroma.schemas.validate_metadata import validate as validate_metadata

    _HAVE_VALIDATOR = True
except Exception:
    _HAVE_VALIDATOR = False

COLLECTION_NAME = "southoftethys"


def git_changed_files(range_spec: str) -> list[Path]:
    cmd = ["git", "diff", "--name-only", range_spec]
    out = subprocess.check_output(cmd, text=True).strip()
    if not out:
        return []
    return [Path(p) for p in out.splitlines() if p.strip()]


def main():
    p = argparse.ArgumentParser(description="Incremental Chroma index updater")
    p.add_argument("--files", nargs="*", help="Paths relative to repo")
    p.add_argument("--git-range", help="Git range (git diff --name-only)")
    p.add_argument("--repo-dir", default=".")
    p.add_argument("--chunk-size", type=int, default=200)
    p.add_argument("--validate", action="store_true")
    p.add_argument(
        "--persist-dir",
        default=os.environ.get("CHROMA_PERSIST_DIR", "storage/chroma"),
    )
    args = p.parse_args()

    repo_root = Path(args.repo_dir).resolve()
    files: list[Path] = []
    if args.git_range:
        files += [repo_root / x for x in git_changed_files(args.git_range)]
    if args.files:
        files += [repo_root / Path(x) for x in args.files]

    # Prefer database/ and snippets/
    files = [
        f
        for f in files
        if f.exists()
        and f.suffix in {".json", ".md", ".txt"}
        and (
            "database" in f.parts
            or "snippets" in f.parts
        )
    ]
    if not files:
        print("No database/ or snippets/ files to index")
        return

    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    if cloud_key:
        client = chromadb.CloudClient(
            api_key=cloud_key,
            tenant=os.environ.get("CHROMA_TENANT"),
            database=os.environ.get("CHROMA_DATABASE"),
        )
    else:
        client = chromadb.PersistentClient(
            path=args.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

    # Must match the full indexer, or upserted chunks land in a different vector space.
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    collection = client.get_or_create_collection(
        COLLECTION_NAME, embedding_function=ef
    )

    ids, docs, metadatas = [], [], []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        payload = None
        if f.suffix == ".json":
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = None
            text = entity_document(payload) if isinstance(payload, dict) else raw
        else:
            text = raw

        for ci, chunk in enumerate(chunk_text(text, args.chunk_size)):
            vid = f"{f.stem}_{ci}"
            meta = build_metadata(
                repo_root, f, payload if isinstance(payload, dict) else None, ci
            )
            if args.validate:
                if not _HAVE_VALIDATOR:
                    raise SystemExit("Validator unavailable")
                try:
                    validate_metadata(
                        "documents",
                        {"id": vid, "text": chunk, "metadata": meta},
                    )
                except Exception as e:
                    print(f"Skipping {vid}: {e}")
                    continue
            ids.append(vid)
            docs.append(chunk)
            metadatas.append(meta)

    if not docs:
        print("No valid chunks to upsert")
        return

    print(f"Upserting {len(docs)} chunks to '{COLLECTION_NAME}'")
    if hasattr(collection, "upsert"):
        collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
    else:
        try:
            collection.delete(ids=ids)
        except Exception:
            pass
        collection.add(ids=ids, documents=docs, metadatas=metadatas)
    print("Upsert completed")


if __name__ == "__main__":
    main()
