# SouthOfTethys Context

## Canon Location

Structured lore lives in **`database/`** (v0.7.0+).
See `database/README.md` and `DESIGN.md` for conventions and roadmap.

## Key Paths

| Path              | Role                                      |
|-------------------|-------------------------------------------|
| `database/`       | Canonical entities, events, bestiary      |
| `AI_CONTEXT.md`   | Large narrative / extraction source       |
| `services/chroma` | Vector index + schemas                    |
| `vidur_portal/`   | Streamlit extraction & query UI           |
| `docs/`           | Published book / GitHub Pages             |
| `timeline/`       | Generated artifacts only (from database/) |

## Deprecated / Removed

- `characters/` (old placeholders) — removed
- `flora_fauna/` (old placeholders) — removed
- legacy `timeline/*.json|md` placeholders — removed; use `database/events/`

Do not reintroduce parallel entity stores.

## Engine Stack

- Chroma + sentence-transformers for retrieval
- Hugging Face model for snippet extraction
- CI publishes timeline, maps, and docs to GitHub Pages
- Docker Compose for local portal + indexer
