# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

The **canon** half of a two-repository project. This repository owns *what exists and what is
true*. The sibling, `4000BCESaraswathy`, is a browser game that owns *what a particular player
did and how it looks*.

That division settles nearly every question that comes up: everything canon holds is a **noun**
— places, species, discoveries, people, words — and everything the game holds is a **verb** or a
**view** — walking, observing, rendering, saving. When something new appears, apply that test
rather than debating it.

Canon is one JSON file per entity under `database/`, validated against JSON Schema in
`database/schemas/`. `database/index.json` is the manifest — **v1.10.0, 497 entities**.

## Commands

```bash
python utils/lint_story.py                     # schemas, index counts, references resolve
python utils/check_playability.py              # can a player actually get to it all
python utils/export_canon_bundle.py --apply    # write the game's data/canon/ bundle
python services/api/build_deploy.py --target vercel   # bundle the retrieval service
```

The first two gate every push. The exporter is a dry run unless you pass `--apply`.

## The rules

**Canon exports canon's own shape.** The game owns the adapters. An earlier design had the
exporter emit the engine's flat `Creature` record, which made this schema hostage to a
TypeScript interface in another repository; inverting that is why six entity types could be
added later without a single Python edit on account of a game change.

**Never hand-edit the game's `data/canon/`.** Change the entity here, re-export. A lock file and
the game's CI enforce it.

**Array order is load-bearing.** The game picks species by indexing into per-biome lists, so
entities carry `source_index` and anything without one sorts last. Reordering silently changes
what lives on somebody's tile.

**Feature branches always.** Never commit to `main` — and this is now enforced rather than
trusted. A ruleset on the default branch blocks direct pushes, force pushes and deletions, and
requires a pull request whose `validate` check has passed. There is **no bypass, for anyone**,
including the repository owner.

That last part has a consequence worth knowing before it bites: if a required check ever hangs
or its workflow breaks, `main` cannot be merged to or repaired until the rule is relaxed. The
recovery is Settings → Rules → Rulesets → *Protect main* → Enforcement: **Disabled**, merge the
fix, then set it back to Active.

**Always end with the pull request link.** Whenever work is pushed, the reply must carry the URL —
the PR if one exists, otherwise the compare link the push prints — so it can be opened directly
rather than described. `gh` is **not installed on this machine**, so the PR usually cannot be
opened for you; hand over the link with a title and body ready to paste:

```
https://github.com/lordlebu/SouthOfTethys/pull/new/<branch>
```

Push before reporting — a link to an unpushed branch 404s. If the work is not ready to push, say
so instead of offering a link.

Only `validate`, from `story-validation.yml`, is required. The jobs in `ci.yml` are deliberately
*not*, because that workflow is path-filtered to `utils/**`, `database/**`, `cartography/**` and
a few others — requiring one would leave a documentation-only pull request pending forever
rather than failing, which is the worse outcome of the two.

**Merging redeploys.** A push to `main` touching `database/` or `services/` rebuilds the search
index, deploys it, and then asks the live `/health` whether its index covers canon. That last
check exists because the service silently served a stale index for two whole field maps while
reporting itself healthy.

## Two things that are easy to get wrong

**`check_playability.py` simulates.** It starts from nothing and repeatedly does whatever has
become possible until nothing more opens. The obvious implementation — "is this requirement
obtainable somewhere?" — passes a dependency cycle, and one shipped. It knowingly duplicates
`holds` and `observed` from the game's `src/journey.ts`; change one, change both.

**A requirement means two different things.** Climbing a rung needs what it stands on to be
*understood*. Forming a reading of a question, or hearing a line, needs only that it has been
*observed*. A hypothesis is built from what you have seen, not what you have finished — and
under one uniform rule the wrong-but-early reading of a question becomes unreachable, which
destroys the mechanic.

## Where the reasoning lives

| File | What it holds |
|---|---|
| `docs/decisions.md` | every call made on the project's behalf, and what is still open |
| `DESIGN.md` | the binding rulings: the era, authored anchors, build-time reading |
| `database/TODO.md` | which entities are missing |
| `database/VALIDATION.md` | what the linters check |

Read `docs/decisions.md` before changing anything structural. It records, among other things,
why `full_moon` and `flood` are never generated, why the landmark loop stays, and why the
Hugging Face model is stock GPT-2 that nothing uses.

## Authoring a field map

Measured across the three that exist: six to eight points of interest, six to nine discoveries
running three to seven rungs, one to three field questions, two or three people, **~1,700 words
of prose**, about twenty JSON entities.

The typing is not the constraint. Each map needs a **thesis** that is not a repeat: Lothal
teaches looking and carries the Mask Family; Narmada shows a record that begins at the wound;
Dwarka is where local knowledge is simply right, and is a cold desert around a harbour whose sea
left inside living memory.

There were four. **The Dry Harbour was retired** because it was a fourth variation on reading the
ground with no story in it — the other three each carry one. Its Glass Scar and Caravan Ground
moved to Dwarka, which is now the only map with desert in its palette. See `docs/decisions.md`.

A field map also declares a **`relief`** — `delta`, `island`, `plateau` or `basin` — which is the
only thing canon says about the *shape* of a map, as distinct from what it is made of. One shaping
rule cannot produce a harbour, an island and a plateau, and trying made every map a dome that was
hardest to walk exactly in the middle where the walking happens.

A region can only hold a map if its biomes are `renderable` in `database/biomes.json`. The
Shattered Sea is the only unbuilt region that qualifies today; the Tethys Sky Routes are blocked
until sky biomes can be drawn, and the Ganges Lava Sea would render as `mountains` until
`lava_field` has a tile.
