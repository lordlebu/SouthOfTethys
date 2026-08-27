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

**Generated timeline artifacts are written straight into `docs/`.** They went to a `timeline/`
build directory that CI copied across, and the copy is exactly what went stale: `docs/` served
"Act 1, Scene 1: The Grove Fire" from an unrelated project for months while the generator was
producing real canon. One tracked location cannot drift from itself, so there is no longer an
intermediate. `timeline/` is gone.

The cartography pipeline is also gone -- `generate_map.py`, `cartography/` and the published
GeoJSON. It drew another project's regions, and `folium` needs real lat/lon that canon does not
have. Geography returns as canon entities first; see `docs/canon-integrity-plan.md`.

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

## Rulings — Varuna's Field Diary

Phase 00 of the plan asked for three answers to be recorded here as rulings rather than
opinions, because content authored against the wrong one has to be rewritten. They were
settled 2026-08-11 and are binding.

**The era is Epoch 5, the last age** — `epoch_post_cataclysm`. Four hundred and eleven years
after the Shattering. This decides who is alive, that the Naraka rifts are open and crossed
through the Dwarka gates, and what Varuna carries. Every field-diary entity authored so far
declares it.

**Field maps are authored anchors on procedural ground.** Canon names a region, its biome
palette and its points of interest; `generateWorld` lays the terrain; `world/fieldMap.ts`
places the anchors. Nobody hand-draws a tilemap, and Garudasaur's Ledge is still a specific
place rather than a cave the generator invented.

**The game reads canon at build time.** The bundle under `data/canon/` is inlined by Vite, so
a malformed file is a build failure rather than a blank panel. The retrieval service is for
cross-referencing and is strictly optional — with `VITE_CANON_API` unset the game makes no
network call at all.

### Deviations from the plan, and why

**There is no `instance` entity type.** The plan named one as the third scale below region.
It became `sub_locations` on a point of interest instead: the gated depths of Kavik's Tower
are the tower, not separate places that happen to sit inside it, and giving them their own
entity would have meant every one carrying a duplicate of its parent's region, epoch and
terrain. `requires` on a sub-location does the gating the plan wanted.

## Contribution Rule

New lore → JSON entity under `database/` with stable ID + update `index.json`.
Narrative prose stays in source docs; structured facts live here.
Species reach the game only through `utils/export_canon_bundle.py` — never by editing the
game's `data/canon/*.json` directly.
