# SouthOfTethys Canonical Database

**Single source of truth** for structured lore.

## Structure

```
database/
├── characters/
├── events/
├── fauna/
├── flora/
├── settlements/
├── regions/
├── artifacts/
├── factions/
├── mythology/
├── timeline/
├── schemas/
└── index.json
```

## Conventions

- Stable IDs: `character_*`, `event_*`, `fauna_*`, etc.
- Cross-references by ID only
- `canon`: `primary` | `secondary` | `draft`

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

Do not recreate parallel entity stores outside this tree.
