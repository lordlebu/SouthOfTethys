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
from pathlib import Path
from typing import Any

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    raise SystemExit(
        "chromadb is required. Install services/chroma/requirements.txt"
    )

try:
    from sentence_transformers import SentenceTransformer
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


def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    words = text.split()
    if not words:
        return [text] if text.strip() else []
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


def entity_document(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, val in payload.items():
        if val is None or val == "" or val == []:
            continue
        if isinstance(val, (dict, list)):
            parts.append(f"{key}: {json.dumps(val, ensure_ascii=False)}")
        else:
            parts.append(f"{key}: {val}")
    return "\n".join(parts)


def build_metadata(repo_root: Path, fpath: Path, chunk_index: int):
    rel = str(fpath.relative_to(repo_root))
    meta: dict[str, Any] = {"source": rel, "chunk_index": chunk_index}
    if fpath.suffix == ".json":
        try:
            payload = json.loads(fpath.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                meta["entity_id"] = payload.get("id", fpath.stem)
                meta["entity_type"] = payload.get("type", fpath.parent.name)
                if payload.get("name"):
                    meta["name"] = payload["name"]
                if payload.get("title"):
                    meta["title"] = payload["title"]
                if payload.get("epoch"):
                    meta["epoch"] = payload["epoch"]
        except Exception:
            meta["entity_id"] = fpath.stem
    else:
        meta["entity_id"] = fpath.stem
    return meta


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
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(COLLECTION_NAME)
    else:
        client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=args.persist_dir,
            )
        )
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(COLLECTION_NAME)

    SentenceTransformer(os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

    ids, docs, metadatas = [], [], []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        if f.suffix == ".json":
            try:
                payload = json.loads(raw)
                text = (
                    entity_document(payload)
                    if isinstance(payload, dict)
                    else raw
                )
            except json.JSONDecodeError:
                text = raw
        else:
            text = raw

        for ci, chunk in enumerate(chunk_text(text, args.chunk_size)):
            vid = f"{f.stem}_{ci}"
            meta = build_metadata(repo_root, f, ci)
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
    if not cloud_key:
        try:
            client.persist()
        except Exception:
            pass
    print("Upsert completed")


if __name__ == "__main__":
    main()
