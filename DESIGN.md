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

## Rulings — geography and eras

Settled 2026-08-27, before any place was entered. All four were cheap to decide then and
expensive afterwards, which is why they were taken first.

**`y` increases southward on the 0-100 grid.** `y = 0` is north. Lothal sits at (28, 50),
Dwarka at (16, 64) — south and west of it — and the Narmada Plateau at (58, 20), the
northernmost of the three. This is the screen convention rather than the latitude one, and it
is chosen because SVG's `y` already grows downward: the game's overworld screen and every atlas
view render the grid directly, with no flip anywhere.

This ratifies rather than invents. `field_map.schema.json` already said it — *"North to south,
screen order — 0 is the top"* — where only the three authors of field maps would ever read it.
The ruling moves it somewhere binding. The reference drawing disagrees:
`dump/Partial_map.png` puts Dwarka north-west of Lothal.
The drawing is a NotebookLM render of the lore and is reference, not authority. The three
coordinates are load-bearing in the shipped game and cannot move; the convention was fitted to
them rather than the other way round.

**A named place that is not walkable is a `place`, not a `settlement`.** `settlement` keeps its
narrow meaning: somewhere people live that canon models in detail. There are two, and each has
a field map. `place` is the fourth tier below region → field map → point of interest, and it is
where the hundreds of named locations across the lore live. Its folder is in `NOT_EXPORTED`
from the commit that created it. `point_of_interest` was the trap worth naming: it already
carries `epochs`, a description and an arrival line, so it looks exactly right — and it is keyed
to a walkable field map and ships to the game.

**An entity with no epoch exists in every era.** Silence means timeless, not unplaced. This
also ratifies an existing line rather than inventing one: `field_map.schema.json` says *"Absent
means the place exists in every era"* on its `epochs` field, and nothing outside that schema
had ever repeated it. It is what fauna already meant too: 346 of the 363 entities without an epoch are species, and that was a
deliberate call — a crocodile is not an era-specific thing. The alternative would have required
dating all 346 before any of them appeared in an atlas at all.

**A place states its identity once and its changes only where they happen.** Coordinates and id
are stated once, because a city does not move. `epochs` carries presence, following the
convention points of interest already use. A per-epoch `states` block is optional and exists for
the few places that genuinely transform — Dwarka is a working harbour in Civilization Dawn and a
drowned gate after the Shattering. Most of several hundred places never change and stay
eight-line files. One entity per place per epoch was rejected: it multiplies hundreds by six and
makes "is this the same place?" unanswerable.

## Contribution Rule

New lore → JSON entity under `database/` with stable ID + update `index.json`.
Narrative prose stays in source docs; structured facts live here.
Species reach the game only through `utils/export_canon_bundle.py` — never by editing the
game's `data/canon/*.json` directly.
