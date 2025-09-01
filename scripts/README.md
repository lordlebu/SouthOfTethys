Incremental indexer helpers for SouthOfTethys

Files
- `index_changes.py` — upserts changed files (or explicit file list) into Chroma (local or cloud).

Quick examples

1) Upsert specific files (local Chroma):

```powershell
python scripts/index_changes.py --files characters/EliaAkaran.json snippets/inbox/queen_envoy.txt
```

2) Upsert files changed in the last commit range:

```powershell
python scripts/index_changes.py --git-range HEAD~1..HEAD
```

3) Upsert to Chroma Cloud (set env vars first):

```powershell
$env:CHROMA_CLOUD_API_KEY = 'ck-...'
$env:CHROMA_TENANT = '8241b0e6-7d0b-41dd-946a-b8954d50714e'
$env:CHROMA_DATABASE = 'Lemuria'
python scripts/index_changes.py --files timeline/timeline.json
```

4) Run validation before upsert (requires `jsonschema` and the schema helper):

```powershell
python scripts/index_changes.py --files timeline/timeline.json --validate
```

Connectivity smoke-test
- Use the `--files` mode on a small file and then query the collection from a Python REPL or via `chromadb` client to ensure vectors are present.
