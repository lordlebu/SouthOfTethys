# SouthOfTethys Canonical Database

**Single source of truth** for structured lore.

## Structure

```
database/
├── characters/     # Stable-ID character entities
├── events/         # Event graph (predecessors / successors)
├── fauna/          # Biological datasets
├── flora/
├── settlements/
├── regions/
├── artifacts/
├── factions/
├── mythology/
├── timeline/       # Epoch definitions
├── schemas/        # JSON Schema definitions
└── index.json      # Master entity index
```

## Conventions

- Stable IDs: `character_*`, `event_*`, `fauna_*`, `flora_*`, etc.
- Cross-references by ID only (no duplicated prose).
- `canon`: `primary` | `secondary` | `draft`
- Sources point back to origin documents (AI_CONTEXT.md, profiles, bestiary text).

## Status (v0.7.0)

| Category    | Count |
|-------------|-------|
| Characters  | 36    |
| Events      | 12    |
| Fauna       | 19    |
| Flora       | 6     |
| Settlements | 2     |
| Regions     | 4     |
| Artifacts   | 1     |
| Factions    | 3     |
| Mythology   | 3     |

## Design Direction

1. `database/` is canonical. Legacy `characters/` and `flora_fauna/` placeholders have been removed.
2. Short-term: validation script + Chroma indexing of these JSON files.
3. Medium-term: expand coverage only where stories/tools need it; keep event graph living.
4. Long-term (optional): richer taxonomies, graph export, query helpers.

Do not recreate parallel entity stores outside this tree.
