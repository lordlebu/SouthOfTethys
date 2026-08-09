# Chroma Service

Builds and persists a Chroma vector index over **canonical** SouthOfTethys lore.

## Source of truth

Indexes:

- `database/characters|events|fauna|flora|settlements|regions|artifacts|factions|mythology/*.json`
- optional `snippets/inbox/*`

Legacy `characters/` and `timeline/` paths are **not** used.

## Run

```bash
docker compose -f docker-compose.chroma.yml up --build
```

Env:

| Variable | Default | Role |
|----------|---------|------|
| `REPO_DIR` | `/app/repo` | Repo mount |
| `CHROMA_PERSIST_DIR` | `/data/chroma` | Local store |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embeddings |
| `CHROMA_CLOUD_API_KEY` | — | Use Chroma Cloud |
| `CHROMA_TENANT` | — | Cloud tenant |
| `CHROMA_DATABASE` | — | Cloud DB |
| `INSERT_VALIDATE` | — | Validate metadata before insert |

## Incremental upsert

```bash
python scripts/index_changes.py --files database/characters/character_kavik.json
python scripts/index_changes.py --git-range HEAD~1..HEAD
```

Collection name: `southoftethys`.

Back up `/data/chroma` regularly; the index is not committed to git.
