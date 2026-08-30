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
`database/schemas/`. `database/index.json` is the manifest — **v1.27.0, 634 entities**.

**Adding anything to canon: read `database/AUTHORING.md` first.** It carries the templates and
the one decision that matters — which folder, because nine of them reach the game and eight
do not.

## Commands

```bash
python utils/lint_story.py                     # schemas, index counts, references resolve
python utils/check_playability.py              # can a player actually get to it all
python utils/check_export_boundary.py          # can lore reach the game by accident
python utils/update_index.py --bump minor      # rebuild index.json ids + counts
python utils/ingest_draft.py <file.md>         # check a drafted chapter before writing it
python utils/generate_timeline_mermaid.py      # docs/timeline_mermaid.md, epochs and events
python utils/generate_atlas.py                 # docs/atlas.md, canon as it stood in each era
python utils/generate_memory_map.py            # docs/memory_map.md, who was there and with whom
python utils/export_canon_bundle.py --apply    # write the game's data/canon/ bundle
python services/api/build_deploy.py --target vercel   # bundle the retrieval service
```

The first three gate every push. The exporter is a dry run unless you pass `--apply`.

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

**One branch at a time, and never `main`.** Work stays on a single feature branch until it
merges. A new piece of work does not get a new branch because it feels separate — it goes on the
branch already open, and the whole lot is reviewed as one pull request. Cut the next branch only
once the previous one has merged.

This is a working rule rather than an enforced one, and it was written after three branches were
left in flight at once — `ingest-draft`, `region-extents` and `north-dwarka` — which made it
impossible to tell what had merged, what was waiting, and which change had caused which failure.
The tidiness of one-change-one-branch is not worth that.

Never commit to `main` — and this is enforced rather than
trusted. A ruleset on the default branch blocks direct pushes, force pushes and deletions, and
requires a pull request whose `validate` check has passed. There is **no bypass, for anyone**,
including the repository owner.

That last part has a consequence worth knowing before it bites: if a required check ever hangs
or its workflow breaks, `main` cannot be merged to or repaired until the rule is relaxed. The
recovery is Settings → Rules → Rulesets → *Protect main* → Enforcement: **Disabled**, merge the
fix, then set it back to Active.

**Large media goes in a git-ignored `dump/`.** The test is what reads the file, not how important
it is: a schema, a script or a workflow reading it means it is tracked, and nothing reading it
means it is a picture a person looks at. `dump/Partial_map.png` is the drawn lore map — the one
this database does not yet model and should — and it sits there at 6.4 MB because no schema, util
or workflow opens it. It is kept on disk, not deleted.

That is not a ranking of lore below code. **Lore is bigger than the game and does not need the
game's permission to exist** — but the database is where canon lives, and a picture of the map is a
picture, not the map. When the geography iteration happens the places on it become entities, and
the PNG stays what it always was: the thing somebody drew first.

`model/` is the deliberate exception at 4.9 MB. `docs/decisions.md` records it as a keep and
`push-hf-model.yml` pushes `model/**` to Hugging Face on change, so it is read by a workflow even
though nothing in the database touches it.

One way this goes wrong: **`git add -A` will sweep up a stray PNG.** That is exactly how the lore
map reached a commit, as a side effect of staging a linter change.

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
*not*, because that workflow is path-filtered to `utils/**`, `database/**` and
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
