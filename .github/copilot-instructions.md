# Working in SouthOfTethys

This file was describing a repository that no longer exists — `timeline/timeline.json`,
`characters/`, `flora_fauna/`, `locations/`, an Ollama extraction step — all of which were
replaced by `database/` some time ago. Anything it said before this rewrite should be treated
as wrong.

## What this repository is

The **canon** half of a two-repository project. It owns what exists and what is true. The other
repository, `4000BCESaraswathy`, is a browser game that owns what a particular player did and
how it looks. The split holds because everything canon holds is a *noun* — places, species,
discoveries, people, words — and everything the game holds is a *verb* or a *view*.

Everything canonical lives in `database/` as one JSON file per entity, validated against JSON
Schema. Index at `database/index.json`, currently **v1.6.0, 504 entities**:

| | |
|---|---|
| **Species** | 256 fauna, 90 flora |
| **World** | 7 regions, 2 settlements, 41 characters, 12 events, 3 factions, 3 artifacts, 3 mythology |
| **Field diary** | 4 field maps, 24 points of interest, 31 discoveries, 8 field questions, 10 NPCs, 10 vocabulary |

## The commands that matter

```bash
python utils/lint_story.py          # schemas, index counts, every cross-reference resolves
python utils/check_playability.py   # can a player actually reach it all — see below
python utils/export_canon_bundle.py --apply   # write the game's data/canon/ bundle
```

The first two run in CI on every push (`.github/workflows/story-validation.yml`) and must pass
before anything merges.

**`check_playability.py` is a simulation, not a set check.** It starts from nothing and
repeatedly does whatever has become possible — climb a rung, hear a line, take a word — until
nothing more opens. Asking instead whether each requirement is "obtainable somewhere" passes a
cycle: A's last rung needs B, B's last rung needs A, both obtainable, neither ever first. That
shipped once. It deliberately duplicates two rules from the game's `src/journey.ts`; if the
semantics change in one, change them in both.

## Rules that are not negotiable

- **Canon exports canon's own shape.** The game owns adapters that translate it. Do not shape a
  schema around a TypeScript interface in another repository.
- **Never edit the game's `data/canon/`.** It is generated. Change the entity here and re-export.
- **Array order is part of the seed contract.** The game indexes into per-biome lists, so
  entities carry `source_index` and unindexed ones sort last — additions cannot reshuffle a
  world somebody already walked.
- **Work on feature branches.** Never commit to `main`.
- **Merging canon redeploys the retrieval service** (`deploy-canon-service.yml`), which rebuilds
  the search index and then checks the live one covers canon.

## Where the reasoning is written down

- `docs/decisions.md` — every call made on the project's behalf and why, plus what is still
  open. Read this before changing anything structural.
- `database/TODO.md` — which entities are missing.
- `DESIGN.md` — the rulings that govern authoring, including the era and how field maps work.
- `CLAUDE.md` — the same ground as this file, for agents that read that name instead.

## Authoring a field map, if that is the task

Six points of interest, six to nine discoveries of three to seven rungs, one to three field
questions, two or three people, and roughly 1,700 words of prose. The typing is not the
constraint — each map needs a *thesis* that is not a repeat of another's, and the four that
exist have used: learning to look, an archive whose record begins at the wound, a place where
local knowledge is simply right, and a place that is out of date rather than mysterious.

Only regions whose biomes are `renderable` in `database/biomes.json` can hold a map. The
Tethys Sky Routes cannot until sky biomes can be drawn.
