# Canon integrity — a plan for `lint_story.py`

> **Published, illustrated version:** [The Check That Skipped](https://claude.ai/code/artifact/1b88dbdd-f20c-48b2-8676-e68b652d289f)
>
> Same content, laid out to be read. Private artifact — it opens for the repository owner and
> whoever they share it with; this file is the authoritative copy.

Canon's lint passes green on three species entered twice, one genus spelled two ways, and eight
fauna with no scientific name. This is what it would take for it to stop doing that.

Everything below is measured against the repository as it stands on **2026-08-24**: 495 entities,
`index.json` v1.9.0, lint reporting success.

---

## The headline: the required check has never validated a schema

`utils/lint_story.py` validates every entity against its JSON Schema — and it wraps that in
`except ImportError`, printing `skipped (jsonschema not installed)` and **returning success** when
the library is missing.

`requirements.txt` does not list `jsonschema`. The `validate` job in `story-validation.yml` installs
that file and nothing else. It is the only required check on `main`.

So the most valuable thing the linter does has been switched off in CI since the day it was written,
and the way it reports that is a line of output nobody reads in a job that goes green.

Locally, where `jsonschema` happens to be installed, all 484 schema-covered entities pass. **Turning
this on is therefore safe** — it is one line in `requirements.txt`, and the reason it is Phase 00 is
that every later phase is worthless until the schemas are actually enforced.

The pattern is worth naming, because it is the same shape as the plate encoder and the fatigue
timeout before it: **a check that silently disables itself is worse than no check**, because it
also removes the pressure to write a real one.

---

## What it checks today, and it is more than you would expect

The linter is not bad. It is 255 lines and it does four things, all as errors:

| Check | What it covers |
|---|---|
| schema | every entity against its type's schema — *when the library is present* |
| index | `index.json` and the files on disk agree **in both directions**, plus counts |
| epochs | any field whose *name mentions* an epoch, not just `epoch` and `epochs` |
| references | any string matching a known id prefix, wherever it appears |

Two of those are genuinely well designed and should survive untouched. The reference walker treats
*any* id-shaped string as a reference, so a new field carrying entity ids is covered the day it is
added rather than the day someone remembers the linter. The epoch check learned the same lesson one
field over, after `epoch_founded` sat unvalidated because the code named `epoch` and `epochs`
explicitly.

**So this plan hardens `lint_story.py`; it does not replace it.** Replacing it would mean rewriting
working reference resolution and index reconciliation in order to arrive at the same place. What is
missing is not a better validator — it is (a) the validator actually running, (b) schemas tight
enough to catch a typo, and (c) a category of check that JSON Schema fundamentally cannot express.

That last point decides the build-or-buy question. `check-jsonschema` and friends validate one file
against one schema. **No off-the-shelf tool checks uniqueness of a field across 257 sibling files**,
and that is precisely the check that would have caught the duplicate species. The cross-file half
has to be hand-written wherever it lives, so it may as well live where the file loading already is.

---

## What it cannot see

### 1. Content invariants — the three duplicate species

Nothing looks at a field's *value* beyond its type. Measured:

| | fauna | flora |
|---|---|---|
| entities | 257 | 90 |
| no `scientific` at all | **8** | 0 |
| binomials used by two entities | **3** | 0 |

The three collisions are *Vulpes gedrosiana*, *Sarasvatimanta gedrosii* and *Vrkshasmara griseus*.
Each pair is one hand-authored entity and one bestiary import of the same animal, distinguishable by
a consistent signature: the authored one has `diet` set with `region` and `source_index` null, the
imported one the reverse.

All six are reachable in the game, so a player meets the same animal under two names — and it is now
visible, because Desert Fox is the most-encountered species in the game and carries a painted plate
while its twin shows an emoji.

### 2. Typos, because the schemas invite them

Ten of eleven schemas set `additionalProperties: true`. Only `region.schema.json` is strict. A
misspelled `scientifc` would validate cleanly and then read as absent everywhere downstream.

Today the damage is small and is not typos: `aliases` on 2 fauna and `crosses_at` on 2 flora are
real fields the schemas never learned about. Both should be added to the schemas rather than
removed from the data.

### 3. Twelve entities no schema covers at all

| folder | entities |
|---|---|
| artifacts | 3 |
| factions | 3 |
| mythology | 3 |
| settlements | 2 |
| timeline | 1 |

`SCHEMA_FOR` has no entry for these, so `validators.get(...)` returns `None` and the loop
`continue`s. They are silently exempt.

### 4. `taxonomy` exists and has never been used

It is in both the fauna and flora schemas as `{"type": "object"}` — no shape, no required keys.
Populated on **8 of 257** fauna and **0 of 90** flora, and inconsistently: some entries key it
`note`, others `notes`, one has `kingdom` and `clade`.

This is the interesting one, and it is a design decision rather than a lint fix. See Phase 03.

---

## What is *not* wrong, and should not be "fixed"

Worth writing down so a later pass does not invent work:

- **`source_index` gaps are deliberate.** 237 of 257 fauna and 70 of 90 flora carry one, and there
  are **zero duplicates**. `CLAUDE.md` states the rule — anything without one sorts last — so the
  40 blanks are the documented behaviour, not a hole. A uniqueness check is worth adding; a
  completeness check is not.
- **The enum-ish fields are already clean.** `rarity` is exactly {common, rare, mythic}, `placement`
  exactly {encounter, flavour, lore}, `canon` is `primary` throughout, and `mood` has nine values
  with no near-duplicates. Constraining them in schema is cheap insurance, not a repair.
- **`diet` is sparse (40 of 347) and that is fine.** It is not required and nothing reads it as
  mandatory.

---

## The phases

Five, ordered by what unblocks what.

### Phase 00 — make the check real

Add `jsonschema` to `requirements.txt`, and **make the missing-library path fail instead of skip**.
A linter that quietly downgrades itself when a dependency is absent will do it again on the next
machine.

*Risk: none measured.* All 484 schema-covered entities already pass locally. Expect CI to stay
green and start meaning something.

**Done when:** `validate` output names a schema count, and removing `jsonschema` from the
environment makes lint exit non-zero rather than pass.

### Phase 01 — close the schema gaps

- Schemas for `artifacts`, `factions`, `mythology`, `settlements`, `timeline`, and the matching
  `SCHEMA_FOR` entries. Twelve entities is small enough to derive the shapes from the data.
- Add `aliases` to the fauna schema and `crosses_at` to flora.
- Flip `additionalProperties` to `false` on all eleven.
- Constrain the enum-ish fields, which is free given they are already consistent.

**Done when:** every entity in `database/` is validated by a schema, and an invented field fails.

### Phase 02 — invariants, and the data they will condemn

The checks JSON Schema cannot express, as a new section of `lint_story.py`:

- `scientific` is unique across fauna and across flora.
- `scientific` is present on every fauna and flora entity.
- `source_index` is unique within a folder where present.
- No two entities share a `name`.

**Sequencing matters here and it is the one trap in this plan.** Each of those checks fails on
today's data the moment it exists. The check and the data fix have to land in the *same* pull
request or `main` cannot merge — and `main` is protected with no bypass, so a red required check is
expensive to unwind.

The data fixes, already scoped:

- **Three merges.** Keep the authored entity — better prompt, `diet` set, and crucially its `id`,
  since `fauna_desert_fox` is what the painted plate is keyed to. Copy `region` and `source_index`
  off the imported twin, delete the twin, update `index.json` counts, re-export.
- **Two renames**, `Silvanus gigas` → `Sylvianus gigas` and `Silvanus pictus` → `Sylvianus pictus`,
  settling one genus on one spelling. The game already accepts both, so nothing breaks either way.
- **Eight binomials** for the fauna that have none.

Two consequences to hold in view while merging:

- Removing three entities reshuffles the per-biome arrays that `source_index` orders, which
  `CLAUDE.md` calls load-bearing: it changes what lives on somebody's tile. Carrying the twin's
  `source_index` onto the survivor keeps the anchor.
- Existing saves reference species ids, so deleting `fauna_gedrosian_desert_fox` orphans it in any
  save that met one.

**Done when:** the four invariants are enforced and the data satisfies them.

### Phase 03 — decide what `taxonomy` is for

The open question, and the only phase that is not obviously worth doing.

Today the game derives an animal's clade by matching keywords against its name and binomial. That is
why an `asuricus` epithet could classify an owl as a spectre, why `camel` made a baby crocodile a
mammal, and why the Iridescent Lothal Silvanus was drawn as a cricket — `Silvanus` is a real-world
beetle genus.

By this project's own noun/verb rule, *what an animal is* is a noun, and nouns are canon's. A
constrained `clade` enum in canon, consumed by the game's adapter, would delete the guessing.

**It is not a small job**: a schema change, ~257 entities to fill, lint, the exporter, and the
game-side adapter, plus a decision about how much taxonomy the fiction wants to commit to. The
counter-argument is real — the classifier now returns zero unknowns and every genus is internally
consistent, so the guessing currently works.

**Recommendation: decide, do not drift.** Either constrain and populate it, or delete the field and
the eight stray objects, so the schema stops advertising something canon does not do. Leaving an
unconstrained `taxonomy` in place is the option that costs the most later.

### Phase 04 — say what is checked, where anybody will look

`database/VALIDATION.md` is dated 2026-08-05 and still lists "Automated JSON-Schema validator
against `database/schemas/` not yet implemented" as deferred. It has been implemented for some time;
it simply never ran. A document describing checks that do not run is worse than no document, and it
is how the Phase 00 bug survived.

Rewrite it as a table of what is enforced, generated from the linter's own check list if that is
cheap, and hand-written if not.

---

## Effort

Honest ranges, in the sitting-shaped units the rendering programme used, which came in at 12.0
against an 11–16 estimate.

| Phase | Sessions | Confidence |
|---|---|---|
| 00 · make the check real | **0.2** | high — one line and one `raise` |
| 01 · close the schema gaps | 1.0–1.5 | high — mechanical, twelve entities and eleven schemas |
| 02 · invariants + the data fixes | 1.5–2.5 | medium — the merges need lore calls, and the re-export has to be verified against the game |
| 03 · `taxonomy` | 0.2 to delete · **3–5** to populate | low — the range *is* the decision |
| 04 · VALIDATION.md | 0.3 | high |
| **Total, without Phase 03** | **3.0–4.5** | |

Phase 00 is worth doing on its own this week whatever happens to the rest.

---

## What this plan does not touch

- `check_playability.py`, which is a different kind of check and is working.
- The exporter, except to re-run it after Phase 02.
- The game repository, except for the adapter if Phase 03 goes the populate route.
- Canon *content* — no new species, regions or maps. This is about whether what exists is
  internally consistent and whether anything would notice if it were not.
