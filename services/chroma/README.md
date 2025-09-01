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

Notes

- Back up `/data/chroma` regularly. The index is not committed to git.
