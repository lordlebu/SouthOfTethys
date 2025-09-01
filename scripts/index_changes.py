#!/usr/bin/env python3
"""Incremental indexer: upsert changed files into Chroma (local or cloud).

Usage patterns:
  - Upsert specific files:
      python scripts/index_changes.py --files characters/EliaAkaran.json snippets/inbox/queen_envoy.txt

  - Upsert files changed in a git range:
      python scripts/index_changes.py --git-range HEAD~1..HEAD

This script validates metadata (optional) and attempts to upsert vectors into the
`southoftethys` collection. It will try `collection.upsert(...)` and fall back to
delete+add if upsert isn't available in the installed chromadb version.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    raise SystemExit(
        "chromadb is required. Install services/chroma/requirements.txt or add chromadb to your environment"
    )

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    raise SystemExit(
        "sentence-transformers is required (pip install sentence-transformers)"
    )

_HAVE_VALIDATOR = False
try:
    from services.chroma.schemas.validate_metadata import validate as validate_metadata

    _HAVE_VALIDATOR = True
except Exception:
    _HAVE_VALIDATOR = False


def git_changed_files(range_spec: str) -> list[Path]:
    cmd = ["git", "diff", "--name-only", range_spec]
    out = subprocess.check_output(cmd, text=True).strip()
    if not out:
        return []
    return [Path(p) for p in out.splitlines() if p.strip()]


def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


def build_metadata_for_file(repo_root: Path, fpath: Path, chunk_index: int):
    rel = str(fpath.relative_to(repo_root))
    meta = {"source": rel, "chunk_index": chunk_index}
    try:
        if rel.startswith("timeline/") and fpath.suffix == ".json":
            payload = json.loads(fpath.read_text(encoding="utf-8"))
            meta.update(
                {
                    "event_id": payload.get("id", fpath.stem),
                    "title": payload.get("title"),
                    "date": payload.get("date"),
                }
            )
        elif rel.startswith("characters/") and fpath.suffix == ".json":
            payload = json.loads(fpath.read_text(encoding="utf-8"))
            meta.update(
                {
                    "character_id": payload.get("id", fpath.stem),
                    "name": payload.get("name", payload.get("id", fpath.stem)),
                }
            )
        elif rel.startswith("snippets/"):
            meta.update({"snippet_id": fpath.stem})
    except Exception:
        # best-effort metadata
        pass
    return meta


def main():
    p = argparse.ArgumentParser(description="Incremental Chroma index updater")
    p.add_argument(
        "--files", nargs="*", help="Paths to files to index (relative to repo)"
    )
    p.add_argument(
        "--git-range",
        help="Git range to collect changed files (git diff --name-only <range>)",
    )
    p.add_argument("--repo-dir", default=".", help="Path to repo root")
    p.add_argument("--chunk-size", type=int, default=200)
    p.add_argument(
        "--validate",
        action="store_true",
        help="Validate metadata against schemas before upsert (requires jsonschema)",
    )
    p.add_argument(
        "--persist-dir",
        default=os.environ.get("CHROMA_PERSIST_DIR", "storage/chroma"),
        help="Local persist dir (if not using cloud)",
    )
    args = p.parse_args()

    repo_root = Path(args.repo_dir).resolve()
    files: list[Path] = []
    if args.git_range:
        files += [repo_root / p for p in git_changed_files(args.git_range)]
    if args.files:
        files += [repo_root / Path(x) for x in args.files]

    # filter supported file types
    files = [f for f in files if f.exists() and f.suffix in {".json", ".md", ".txt"}]
    if not files:
        print("No files to index")
        return

    # Connect to Chroma (cloud if API key available)
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    collection_name = "southoftethys"
    if cloud_key:
        tenant = os.environ.get("CHROMA_TENANT")
        database = os.environ.get("CHROMA_DATABASE")
        client = chromadb.CloudClient(
            api_key=cloud_key, tenant=tenant, database=database
        )
        try:
            collection = client.get_collection(collection_name)
        except Exception:
            collection = client.create_collection(collection_name)
    else:
        client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet", persist_directory=args.persist_dir
            )
        )
        try:
            collection = client.get_collection(collection_name)
        except Exception:
            collection = client.create_collection(collection_name)

    embed_model = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    SentenceTransformer(embed_model)

    ids, docs, metadatas = [], [], []
    for f in files:
        text = f.read_text(encoding="utf-8")
        chunks = chunk_text(text, chunk_size=args.chunk_size)
        for ci, chunk in enumerate(chunks):
            vid = f"{f.stem}_{ci}"
            meta = build_metadata_for_file(repo_root, f, ci)
            payload = {"id": vid, "text": chunk, "metadata": meta}
            if args.validate:
                if not _HAVE_VALIDATOR:
                    raise SystemExit(
                        "Validation requested but validate_metadata helper not available. Install jsonschema and ensure services.chroma.schemas is importable."
                    )
                try:
                    validate_metadata(
                        (
                            "events"
                            if str(f).startswith(str(repo_root / "timeline"))
                            else (
                                "characters"
                                if str(f).startswith(str(repo_root / "characters"))
                                else (
                                    "snippets"
                                    if str(f).startswith(str(repo_root / "snippets"))
                                    else "documents"
                                )
                            )
                        ),
                        payload,
                    )
                except Exception as e:
                    print(f"Skipping {vid} due to validation error: {e}")
                    continue
            ids.append(vid)
            docs.append(chunk)
            metadatas.append(meta)

    if not docs:
        print("No valid chunks to upsert after validation")
        return

    # Attempt upsert
    try:
        print(
            f"Attempting upsert of {len(docs)} chunks to collection '{collection_name}'"
        )
        # Some chromadb versions expose upsert, others do not
        if hasattr(collection, "upsert"):
            collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
        else:
            # fallback: delete then add
            try:
                collection.delete(ids=ids)
            except Exception:
                pass
            collection.add(ids=ids, documents=docs, metadatas=metadatas)
        if not cloud_key:
            try:
                client.persist()
            except Exception:
                pass
        print("Upsert completed")
    except Exception as e:
        raise SystemExit(f"Failed to upsert to Chroma: {e}")


if __name__ == "__main__":
    main()
