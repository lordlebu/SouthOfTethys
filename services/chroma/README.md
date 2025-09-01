# Chroma Service

This folder contains a dedicated service for building and persisting a Chroma vector index for SouthOfTethys.

Usage

- Build the service via the top-level docker-compose (recommended):
  ```bash
  docker compose -f docker-compose.chroma.yml up --build
  ```

- The service expects the repository mounted into `/app/repo` and writes Chroma storage to `/data/chroma`.

Environment variables

- `REPO_DIR` — path to the repo inside container (default: `/app/repo`).
- `CHROMA_PERSIST_DIR` — path to persist Chroma store (default: `/data/chroma`).
- `EMBEDDING_MODEL` — sentence-transformers model to use.

Cloud integration

The indexer supports Chroma Cloud. To use it, set the following env vars instead of local persistence:

- `CHROMA_CLOUD_API_KEY` — your Chroma Cloud API key (store securely, do not commit).
- `CHROMA_TENANT` — optional tenant id for your cloud account.
- `CHROMA_DATABASE` — optional database name (provider-specific).

Example (docker compose override):

```yaml
  chroma-service:
    environment:
      - CHROMA_CLOUD_API_KEY=${CHROMA_CLOUD_API_KEY}
      - CHROMA_TENANT=${CHROMA_TENANT}
      - CHROMA_DATABASE=${CHROMA_DATABASE}
```

Notes

- Back up `/data/chroma` regularly. The index is not committed to git.
