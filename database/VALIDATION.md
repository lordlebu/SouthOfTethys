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
| **schema** | All 494 entities against 15 schemas. Every entity folder has one. |
| **strict fields** | `additionalProperties: false` on all 15, so a misspelled `scientifc` fails by name instead of reading as absent. |
| **index, both ways** | Every id in `index.json` has a file, every file is in `index.json`, and the per-category counts match. |
| **epochs** | Any field whose *name* mentions an epoch resolves to `timeline/epochs.json` — not just `epoch` and `epochs`, because `epoch_founded` once sat unvalidated one field over. |
| **references** | Any string matching a known id prefix resolves to an entity that exists, wherever it appears in the tree. |
| **clade** | Every fauna states one, from the sixteen in `database/clades.json`. Required, so a new species cannot ship without saying what it is. |
| **subclade** | Where given, it must be a sub-group of *that* clade. A cross-field dependency, so it lives in the linter: JSON Schema checks each field against a flat enum and would let a bird be a dromaeosaurid. |
| **unique binomial** | No two fauna, and no two flora, share a `scientific`. |
| **unique name** | No two entities *in the same folder* share a `name`. Across folders is allowed and correct: `Dwarka` is both a settlement and the field map of it. |
| **unique source_index** | Within a folder, where present. Blanks are fine — the documented rule is that anything without one sorts last. |
| **binomial present** | Every fauna and flora has one. |
| **the linter's own dependency** | A missing `jsonschema` exits non-zero. It used to print a note and report success. |
| **overworld anchors** | The three field-map coordinates the game's overworld screen is laid out from — Lothal (28, 50), Dwarka (16, 64), Narmada (58, 20) — match `OVERWORLD_ANCHORS` in the linter. Moving one crashes nothing; it silently rescales that screen, and the geometry tests in both repositories check the arithmetic rather than the data. |
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

`canon_version` is not sufficient for any of this. Canon `main` and `feat/flora-growth-forms` both
declare `1.11.0` and produce a different `species.json`, and it is the branch's copy that is
committed in the game today. A version nobody bumps identifies nothing; hashes do.

Constrained by enum where the data was already consistent: `rarity`, `placement`, `canon`, `diet`.
`mood` was already an enum of eleven values before this pass and was left untouched — an earlier
draft of this file said it had been "deliberately left open", which was simply wrong about a file
it was describing. Exactly the failure mode this document exists to avoid.

## Not enforced — known, and why

| Gap | Status |
|---|---|
| **Flora clades** | All 256 fauna state their clade; the 90 flora do not. Their growth form is still derived from names game-side, exactly the way body plans were before this. |
| **`taxonomy` shape** | Still `{"type": "object"}` with no required keys, on 9 of 256 fauna. Left free on purpose: Phase 03 answered the part that mattered with a real `clade` field, and what remains here is genuinely editorial notes. |
| **Geography beyond field maps** | Field maps carry `coordinates`; the ~15 other places on the lore map are not entities at all. Deliberate, and sequenced — see `docs/canon-integrity-plan.md`. |
| **Large media placement** | Nothing checks that a big binary sits in the git-ignored `dump/` rather than tracked. A 6.4 MB lore map reached a commit through `git add -A`. The rule is in `CLAUDE.md`; a size check in lint would enforce it and has not earned its place — one accident is not a pattern, and a linter that failed on a file somebody deliberately tracked would be worse than the accident. |
| **Spouse field** | Sometimes an array, sometimes a string. The schema stays permissive; long-standing and non-blocking. |

## The rule this file exists to enforce on itself

**A check that silently disables itself is worse than no check**, because it also removes the
pressure to write a real one. If a check here cannot run, it should fail loudly — and if this table
and the linter ever disagree, the linter is right and this file is the bug.
