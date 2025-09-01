#!/usr/bin/env python3
"""Diagnostic helper to verify Chroma Cloud connectivity and collection contents.

Usage:
  Set env vars: CHROMA_CLOUD_API_KEY, CHROMA_TENANT (optional), CHROMA_DATABASE (optional)
  Then run:
    python scripts/check_chroma_cloud.py

This prints available collections and for the configured collection (southoftethys) prints a small sample count.
"""
from __future__ import annotations

import os

try:
    import chromadb
except Exception:
    print(
        "chromadb package not found. Install services/chroma/requirements.txt or pip install chromadb"
    )
    raise SystemExit(2)


def main():
    api_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    if not api_key:
        print("CHROMA_CLOUD_API_KEY not set. Set it and retry.")
        raise SystemExit(2)

    tenant = os.environ.get("CHROMA_TENANT")
    database = os.environ.get("CHROMA_DATABASE")
    collection_name = os.environ.get("CHROMA_COLLECTION_NAME", "southoftethys")

    print(f"Connecting to Chroma Cloud (database={database}, tenant={tenant})...")
    try:
        client = chromadb.CloudClient(api_key=api_key, tenant=tenant, database=database)
    except Exception as e:
        print(f"Failed to construct CloudClient: {e}")
        raise SystemExit(2)

    # list collections if possible
    try:
        cols = None
        if hasattr(client, "list_collections"):
            cols = client.list_collections()
        elif hasattr(client, "get_collections"):
            cols = client.get_collections()
        print("Collections available:")
        if cols:
            try:
                # normalize display
                for c in cols:
                    if isinstance(c, dict):
                        print(" -", c.get("name") or c.get("id") or str(c))
                    else:
                        print(" -", str(c))
            except Exception:
                print(cols)
        else:
            print("  (no collections returned or client does not expose listing)")
    except Exception as e:
        print(f"Failed to list collections: {e}")

    # try to inspect the expected collection
    try:
        print(f"Inspecting collection '{collection_name}'...")
        coll = client.get_collection(collection_name)
        # attempt to retrieve a small sample
        try:
            res = coll.get(limit=5)
            ids = res.get("ids") if isinstance(res, dict) else None
            print(
                f"Collection '{collection_name}' sample size: {len(ids) if ids is not None else 'unknown'}"
            )
        except Exception as e:
            print(f"Unable to call get() on collection: {e}")
    except Exception as e:
        print(f"Collection '{collection_name}' not found or cannot be opened: {e}")


if __name__ == "__main__":
    main()
