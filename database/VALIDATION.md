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
| **schema** | All 497 entities against 15 schemas. Every entity folder has one. |
| **strict fields** | `additionalProperties: false` on all 15, so a misspelled `scientifc` fails by name instead of reading as absent. |
| **index, both ways** | Every id in `index.json` has a file, every file is in `index.json`, and the per-category counts match. |
| **epochs** | Any field whose *name* mentions an epoch resolves to `timeline/epochs.json` — not just `epoch` and `epochs`, because `epoch_founded` once sat unvalidated one field over. |
| **references** | Any string matching a known id prefix resolves to an entity that exists, wherever it appears in the tree. |
| **clade** | Every fauna states one, from the sixteen in `database/clades.json`. Required, so a new species cannot ship without saying what it is. |
| **subclade** | Where given, it must be a sub-group of *that* clade. A cross-field dependency, so it lives in the linter: JSON Schema checks each field against a flat enum and would let a bird be a dromaeosaurid. |
| **the linter's own dependency** | A missing `jsonschema` exits non-zero. It used to print a note and report success. |

Constrained by enum where the data was already consistent: `rarity`, `placement`, `canon`, `diet`.
`mood` was already an enum of eleven values before this pass and was left untouched — an earlier
draft of this file said it had been "deliberately left open", which was simply wrong about a file
it was describing. Exactly the failure mode this document exists to avoid.

## Not enforced — known, and why

| Gap | Status |
|---|---|
| **Duplicate binomials** | Three pairs share one `scientific`: *Vulpes gedrosiana*, *Sarasvatimanta gedrosii*, *Vrkshasmara griseus*. Each is one hand-authored entity and one bestiary import of the same animal. JSON Schema cannot express uniqueness across sibling files, so this needs a hand-written invariant. See `docs/canon-integrity-plan.md`, Phase 02. |
| **Missing binomials** | Eight fauna have no `scientific` at all. |
| **`taxonomy` shape** | Still `{"type": "object"}` with no required keys, and still an editorial scratchpad. Phase 03 resolved the part that mattered by adding `clade` as a real field rather than constraining this one; what is left here is genuinely notes. |
| **Flora clades** | Fauna all carry one; the 90 flora do not. `growth_form` is derived from names game-side, the same way body plans used to be. |
| **Spouse field** | Sometimes an array, sometimes a string. The schema stays permissive; long-standing and non-blocking. |

## The rule this file exists to enforce on itself

**A check that silently disables itself is worse than no check**, because it also removes the
pressure to write a real one. If a check here cannot run, it should fail loudly — and if this table
and the linter ever disagree, the linter is right and this file is the bug.
