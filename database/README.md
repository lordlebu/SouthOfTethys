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

## Species placement, and what empty `biomes` means

Fauna and flora carry game-facing fields — `biomes`, `placement`, `rarity`, `mood`,
`journal_prompt` — that `utils/export_game_data.py` projects into the game. `placement`
decides whether a species is ever met:

| placement | meaning |
|-----------|---------|
| `encounter` | a creature the player can meet on a tile |
| `flavour`   | a plant that dresses a tile |
| `lore`      | authored, described, never placed |

**An empty `biomes` list is ambiguous, and that ambiguity has already caused one wrong
call.** It can mean *nobody has tagged this yet*, or it can mean *this is deliberately
held out of play*. Before filling one in, check for `placement_note`: if that field is
present, the emptiness is a decision and the note explains it.

Currently 85 species are `lore`. Three groups, three different reasons:

- **Sky species** (`region_tethys_sky_routes`, 40) — the floating islands have no
  equivalent among the ten ground biomes. Inert until the game models sky at all.
- **Asura conjurations** (21) — the cozy pillar frames creatures as neighbours to be
  observed, and these are horror. Whether they are encounterable, journal-only, or gated
  behind a later mode is an open design question (`docs/bestiary.md`, Open Questions #4).
- **Individually held** (3) — `fauna_cognitavi` is a sovereign people rather than
  wildlife; `fauna_megalosaurus` is a specific Naraka portal event creature;
  `fauna_tendua_manticore` is Asura-born. Each carries a `placement_note`.

Sentient species carry `sentient: true`. They are sovereign cultures — the Cognitavi,
Silvanus and Sylvian lineages, Nagaraptor, Vajraptor — and should not sit in the random
encounter table untagged. Several still do, inherited from the bestiary import; that is
a known open question, not an endorsement.

## Status (v1.1.0)

| Category    | Count |
|-------------|-------|
| Characters  | 41    |
| Events      | 12    |
| Fauna       | 256   |
| Flora       | 90    |
| Settlements | 2     |
| Regions     | 7     |
| Artifacts   | 3     |
| Factions    | 3     |
| Mythology   | 3     |

Counts are generated — `index.json` is authoritative and `utils/lint_story.py` checks it
against the files. Note that check runs one way only, index → files, so an orphaned entity
file is invisible to it.

Do not recreate parallel entity stores outside this tree. The game's
`data/creatures.json` and `data/flora.json` are a generated projection of this database,
not a second store — see `utils/export_game_data.py`.
