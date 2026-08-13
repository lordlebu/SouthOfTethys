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
`journal_prompt` — that `utils/export_canon_bundle.py` projects into the game. `placement`
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

The remaining `lore` species are held for two settled reasons, not as a backlog:

- **Sky species** (`region_tethys_sky_routes`, 41) — reserved. The floating islands are a
  planned future mode with their own biomes, and these are its content, waiting. They are
  not untagged; do not tag them into ground biomes to "use them up".
  `fauna_asura_tainted_gargoyle` is filed here rather than with the Asura set, because it
  lives on the islands' undersides.
- **Individually held** (2) — `fauna_megalosaurus` is a specific Naraka portal event
  creature rather than ambient fauna, and `fauna_tendua_manticore` is bound to the
  desecration of Kavik's tower. Both carry a `placement_note`.

**The Asura-tainted species are placed, on purpose.** They are met occasionally and are
meant to unsettle — the taint follows civilisation, so the odds are highest near
settlements (~11%) and low in open country (under 3%). This works only because `rarity`
is weighted: see `weightByRarity` in the game's `src/content/species.ts`, and the tests
that lock those rates. Before the weighting existed, uniform picking put a horror in every
second village.

**`sentient` is taxonomy, not a placement rule.** It marks the avian-dinosaurid and other
sapient lineages — Cognitavi, Nagaraptor, Vajraptor, Silvanus, Sylvians, Kuktush. In-world
the Harappans regard them as animals, so a sentient species in the encounter table is
correct and should not be "fixed".

## Status (v1.6.0 — 504 entities)

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
The game's `data/canon/` bundle — `species.json`, `places.json`, `knowledge.json` and a lock
file — is a generated projection of this database, not a second store. See
`utils/export_canon_bundle.py`. It exports *canon's* shape; the game owns adapters under
`src/content/` that turn it into engine structures, so a change to the engine's types never
reaches back into a schema here.
