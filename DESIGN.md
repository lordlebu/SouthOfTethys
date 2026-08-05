# SouthOfTethys Design & Roadmap

## Core Principle

**`database/` is the single source of truth** for structured canon.
All tools (Vidur Portal, Chroma, publishing pipeline, future generators) should read from it.

## Architecture (Hybrid Continuity)

```
AI_CONTEXT.md / narrative sources
        ↓ extraction
database/   ← canonical JSON entities + event graph
        ↓
Chroma index / Vidur Portal / CI publishing / maps
```

Legacy placeholder directories (`characters/`, `flora_fauna/`, top-level `timeline/`) have been removed.
Event data lives under `database/events/` and epoch definitions under `database/timeline/`.
CI/map scripts that previously read `timeline/` should be pointed at `database/`.

## Original Plan → Current Mapping

| Original Phase              | Status                          |
|----------------------------|---------------------------------|
| Core schemas               | Partial (character/event/fauna) |
| Entity extraction          | Strong (v0.7.0 coverage)        |
| Stable IDs + dedup         | Done                            |
| Relationship / event graph | Living, core Lothal chain linked|
| Taxonomies                 | Light (enough for use)          |
| Search index               | Chroma exists; needs rewiring   |
| World graph / queries      | Future                          |

## Near-term Priorities

1. **Validation** – script that checks ID existence, broken refs, index consistency.
2. **Chroma wiring** – index `database/**/*.json` so Portal/HF model use real lore.
3. **Selective expansion** – missing artifacts (Mask of Tethys, etc.), Narmada University as settlement, more flora only when needed.
4. **Keep event graph living** – add edges when stories require them.

## Out of Scope for Now

- Full biological taxonomy overhaul
- Separate graph database
- Re-creating parallel entity folders

## Contribution Rule

New lore → JSON entity under `database/` with stable ID + update `index.json`.
Narrative prose stays in source docs; structured facts live here.
