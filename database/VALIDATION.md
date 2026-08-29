# What is checked, and what is not

`python utils/lint_story.py` — run by the `validate` job on every push, and the only required check
on `main`.

This file used to be a report from one branch in August 2026, and its last line of substance said
the JSON-Schema validator was "not yet implemented". It had been implemented for some time. What it
had never done was **run**: the check was wrapped in `except ImportError`, `requirements.txt` did
not list `jsonschema`, and the job installed that file and nothing else. So a document describing
checks that did not run helped a missing check survive.

It is now a list of what is enforced, which is a thing that can be checked against reality.

## Enforced — lint fails

| Check | Covers |
|---|---|
| **schema** | All 552 entities against 16 schemas. Every entity folder has one. |
| **strict fields** | `additionalProperties: false` on all 16, so a misspelled `scientifc` fails by name instead of reading as absent. |
| **index, both ways** | Every id in `index.json` has a file, every file is in `index.json`, and the per-category counts match. |
| **epochs** | Any field whose *name* mentions an epoch resolves to `timeline/epochs.json` — not just `epoch` and `epochs`, because `epoch_founded` once sat unvalidated one field over. |
| **references** | Any string matching a known id prefix resolves to an entity that exists, wherever it appears in the tree. |
| **clade** | Every fauna states one, from the sixteen in `database/clades.json`. Required, so a new species cannot ship without saying what it is. |
| **growth form** | Every flora states one, from the fourteen in `database/growth_forms.json`. Required, and the value is checked against that file as well as the schema — the two can drift apart otherwise. |
| **subclade** | Where given, it must be a sub-group of *that* clade. A cross-field dependency, so it lives in the linter: JSON Schema checks each field against a flat enum and would let a bird be a dromaeosaurid. |
| **unique binomial** | No two fauna, and no two flora, share a `scientific`. |
| **unique name** | No two entities *in the same folder* share a `name`. Across folders is allowed and correct: `Dwarka` is both a settlement and the field map of it. |
| **unique source_index** | Within a folder, where present. Blanks are fine — the documented rule is that anything without one sorts last. |
| **binomial present** | Every fauna and flora has one. |
| **the linter's own dependency** | A missing `jsonschema` exits non-zero. It used to print a note and report success. |
| **overworld anchors** | The three field-map coordinates the game's overworld screen is laid out from — Lothal (28, 50), Dwarka (16, 64), Narmada (58, 20) — match `OVERWORLD_ANCHORS` in the linter. Moving one crashes nothing; it silently rescales that screen, and the geometry tests in both repositories check the arithmetic rather than the data. |
| **whereabouts resolve** | `location` and `field_map` point at an entity that exists. Resolved by field *name*, not by id shape: the generic reference check only sees strings matching a known prefix, so a bare `ironfang_mountains` was never yielded to it. Five event locations sat in canon that way — looking exactly like references, invisible to the check that resolves references. |
| **bestiary slug** | A species' `region` is one a region actually declares as its `bestiary_region`. Two non-geographic buckets are named in the linter as known exceptions rather than silently allowed. |
| **culture declared** | A `culture` is one of those in `database/cultures.json`. It was 25 free-text values across 51 characters with nothing checking any of them, which is how `asura` came to mean a culture, a species and a creature prefix at the same time. |
| **subclade enum agrees with the tree** | The flat `subclade` enum in `fauna.schema.json` matches the union of what `clades.json` declares. They live in different files and drifted the moment `construct` gained sub-groups: the tree allowed `ember_born` and the schema rejected it, which reads as the entity being wrong rather than the two lists disagreeing. |
| **base_species resolves** | Where a creature names the animal it was made from, that animal exists and is not itself. |
| **unique event title** | No two events share a title, compared loosely — case, and a leading `the`/`a`/`an`, are not what makes two events different. The uniqueness check above reads `name` and an event carries `title`, so events had never been covered: a generated chapter proposed "The Shadow Pact of Saraswati" while canon held "Shadow Pact of Saraswati", same two participants, and nothing would have caught it. |
| **guide templates** | Every complete JSON template in `database/AUTHORING.md` validates against its schema. The guide's first version told authors to write `"status": "living"` on a character, which is not one of the four values allowed — the exact mistake it exists to prevent. A document that can drift from the schemas will. |
| **sample isolation** | An entity marked `sample: true` may be referenced by another sample and by nothing else. The Dragon's Spine episode — an event, the king, the dragon and the range — is kept as a test fixture, and this is what keeps it deletable with a four-file `git rm` instead of quietly becoming load-bearing. |
| **event edges, both ends** | An edge stated as a `successor` is stated as a `predecessor` too, and vice versa. Only `successors` is read when the timeline is drawn, so an edge declared on the predecessor side alone exists in canon and never appears in the picture. |

## The export boundary — `utils/check_export_boundary.py`

A second gate, run beside the linter in `story-validation.yml`. The linter asks whether canon is
consistent; this asks whether canon can reach the game by accident.

| Check | What it means |
|---|---|
| **every folder classified** | Each directory under `database/` is named in `BUNDLE` or in `NOT_EXPORTED`. A folder in neither is an error, because the natural way to add a new entity type is to create the folder and never think about the exporter again — and the lore layer is about to grow by hundreds of entities that are not meant to ship. |
| **no folder on both sides** | Nothing is exported and withheld at once. |
| **no phantom folder** | `BUNDLE` cannot name a directory that does not exist; the typo exports nothing and reads as "that data was empty". |
| **bundle fingerprint** | The bundle the exporter *would* write still hashes to `database/export.lock.json`. An intended change is re-pinned with `--update`, deliberately, in the same commit. |
| **drift against the game** | Reported, never fatal, and skipped in CI where the sibling repository is not checked out. It is what catches a bundle exported from a branch that never merged. |

`canon_version` is not sufficient for any of this, and the case that proved it has since played
out. `main` and `feat/flora-growth-forms` both declared `1.11.0` while producing a different
`species.json`, and it was the branch's copy that sat committed in the game. A version nobody bumps
identifies nothing; hashes do.

That branch has now merged, and the fingerprint did exactly what it exists for: 90 flora gaining a
`growth_form` moved `species.json`, the check failed with the file named, and the pin was updated
deliberately rather than drifting unnoticed. **A failure here is usually correct.** It means a lore
change reached the game's data — re-pin with `--update` when that was the intent, and look harder
when it was not.

Constrained by enum where the data was already consistent: `rarity`, `placement`, `canon`, `diet`.
`mood` was already an enum of eleven values before this pass and was left untouched — an earlier
draft of this file said it had been "deliberately left open", which was simply wrong about a file
it was describing. Exactly the failure mode this document exists to avoid.

## Not enforced — known, and why

| Gap | Status |
|---|---|
| **`taxonomy` shape** | Still `{"type": "object"}` with no required keys, on 9 of 256 fauna. Left free on purpose: Phase 03 answered the part that mattered with a real `clade` field, and what remains here is genuinely editorial notes. |
| **Place coordinates** | No `place` carries any, and the atlas draws a map for one era out of six. Not a gap and not pending: the only grid canon holds describes the world after the Great Shattering, and the Shattering is **withheld on purpose** — canon keeps its consequences and not its account, because arriving at it is what the player is there to do. Ruling in `DESIGN.md`. Nothing checks that a place is eventually placed, because most never will be. |
| **Large media placement** | Nothing checks that a big binary sits in the git-ignored `dump/` rather than tracked. A 6.4 MB lore map reached a commit through `git add -A`. The rule is in `CLAUDE.md`; a size check in lint would enforce it and has not earned its place — one accident is not a pattern, and a linter that failed on a file somebody deliberately tracked would be worse than the accident. |
| **Corals filed as flora** | Canon's two *Tethysolithus* reef-builders are cnidarians — animals — and sit in `database/flora/`. They carry `growth_form: coral` so the database stops implying they are plants, but moving them to `fauna` with a `clade` is a canon decision nobody has made. |
| **`region` on 46 species is not a place** | 40 carry `asura-conjurations` — a real grouping, by what made them rather than where they live, and arguably a faction or a tag rather than a region. 6 carry `prototype-starters`: a cloud antelope, a hill macaque, a monsoon crane, a painted deer and two others, still labelled from development. Those look like leftovers. Both are allowlisted so a *typo* still fails, and neither is changed here, because `region` is exported — moving them edits the game's bundle and is a canon decision, not a lint's. |
| **`habitats` mixes ids with descriptors** | 99 habitat entries across fauna and flora; 19 of them, in 5 distinct values, are not entities. Two name places (`tethys`, `hyrkanian_steppe`) and three are descriptors that never will be — `coastal` (8), `canopy` (4), `corrupted_zones` (2). Not added to the whereabouts check, because fixing 2 of 19 would be arbitrary and `habitats` is exported: the game falls through to it when a species states no `region`, so changing it edits the bundle. Splitting geography from description is the fix, and it is a canon call. |
| **`origin` on a faction means two things** | Sometimes a place (`mohenjo_daro`, now `place_mohenjodaro`), sometimes an ancestry (`vedda_naga_hybrid`). Left out of the whereabouts check for that reason. Splitting it into two fields would be the fix. |
| **Spouse field** | Sometimes an array, sometimes a string. The schema stays permissive; long-standing and non-blocking. |

## The rule this file exists to enforce on itself

**A check that silently disables itself is worse than no check**, because it also removes the
pressure to write a real one. If a check here cannot run, it should fail loudly — and if this table
and the linter ever disagree, the linter is right and this file is the bug.
