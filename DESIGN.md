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

## The game is a viewer for the canon

`4000BCESaraswathy` — *South of Tethys: Jambhudweepa Adventure* — is not a separate
product that happens to share a setting. **The canon and the published book are the
primary work; the game is the beautiful way to browse them.** The walk is an interface.

That settles a question the bestiary raised and left open for a long time: 300-odd species
against an MVP asking for six. Scale is a *feature*, not a problem to curate away. Breadth
is the point, and the encounter tables should keep reaching for more of the canon rather
than narrowing to a tasteful subset.

Consequences worth stating, because they are easy to get backwards:

- Species are added to canon first, always. The game receives them by export.
- A species that cannot yet be placed is not waste — it is in the book and answerable by
  the portal. `placement: "lore"` is a real state, not a backlog.
- The two published sites are halves of one thing: the book at `lordlebu.github.io/SouthOfTethys`
  and the walk at `lordlebu.github.io/4000BCESaraswathy`.

## Contribution Rule

New lore → JSON entity under `database/` with stable ID + update `index.json`.
Narrative prose stays in source docs; structured facts live here.
Species reach the game only through `utils/export_game_data.py` — never by editing the
game's `data/*.json` directly.
