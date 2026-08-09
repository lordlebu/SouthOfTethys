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

Legacy placeholder directories (`characters/`, `flora_fauna/`, top-level placeholder `timeline/` files) have been removed.
Event data lives under `database/events/`.
Generated timeline artifacts are written to `timeline/` by utility scripts.

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

1. **Validation** – `utils/lint_story.py` against `database/`
2. **Chroma wiring** – index `database/**/*.json`
3. **Selective expansion** – Mask of Tethys, Narmada University, etc.
4. **Keep event graph living** – add edges when stories require them

## Contribution Rule

New lore → JSON entity under `database/` with stable ID + update `index.json`.
Narrative prose stays in source docs; structured facts live here.
