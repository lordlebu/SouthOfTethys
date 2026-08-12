# Decisions and open calls

Choices made across the two repos that the code cannot explain on its own, and the questions
still waiting on a human.

`ROADMAP_NEXT.md` is what happens next. `database/TODO.md` is which entities are missing. This
is *why things are the way they are*, and what I decided on my own authority that someone
should check.

Both repos are on `feature/canon-bundle`.

---

## Decisions taken

**Canon exports canon's shape; the game adapts it.** The exporter emits `species/places/
knowledge/world.json` in canon's own vocabulary, and the game owns `src/content/*.ts` to
translate. The earlier direction — canon emitting the engine's `Creature`/`Flora` shape — made
canon's schema hostage to a TypeScript interface in another repo.

**A requirement means two different things, on purpose.** Climbing a rung requires what it
stands on to be *fully understood*; forming a reading of a field question requires only that
the evidence has been *observed* (rung ≥ 1). A hypothesis is built from what you have seen, not
from what you have finished. Under one uniform rule, `question_silver_water`'s moon reading —
which exists to be available early and wrong — was gated behind already being right.

**Weather is engine-side and seed-derived.** Same seed, same sky at the same hour, for every
player. `world/weather.ts` takes an hour count rather than a timestamp so it does not depend on
`game/dayNight.ts`, keeping the layering one-way.

**`full_moon` and `flood` are in canon's weather enum and are not generated.** One is a phase
of the moon, the other a state of the land. Rolling them out of a weather table would make
`question_silver_water`'s moon reading true by coincidence, which is the thing that question is
about. Either needs its own model to be gateable.

**Two clocks, two vocabularies, one explicit mapping.** `dayNight.ts` labels the sky for the
journal (`first light`, `noon`); canon enumerates `dawn | morning | afternoon | evening |
night`. `game/moment.ts` maps between them in a written-out table. `noon` folds into `afternoon`
because canon has no midday. A raw sky label passed into a condition check matches nothing and
fails silently.

**Field maps seed from their own id.** Lothal is the same Lothal for every player — a
documented island, not a roguelike.

**`saveJourney` takes `progress` optionally.** It defaults to the stored value, so the data
layer could land without editing `App.tsx` and the UI instance can adopt it whenever.

**Species calls made on my reading of the lore**, each reversible:
- *Cognitavi* treated as an avian dinosaurid, following the user's correction.
- Naraka creatures reach this realm through the Dwarka gates, which is what `crosses_at`
  records; Megalosaurus was reclassified on that basis.
- `Estemmenosuchus Executioner` moved on my reading alone — worth a second opinion.
- Asura settlement rate sits at 11.1%. That number is my calibration, not canon.

---

## Open — needs a human call

| Question | Why it is open |
|---|---|
| Should `climate` be a field on the field map? | Weather weights are hardcoded in the engine (`clear 58 / mist 18 / rain 18 / storm 6`). A delta and the Gedrosian desert should not share a sky. Moving it to canon is a schema change plus an export change. |
| Where does `full_moon` belong? | It is in the `weather` enum but is not weather. Probably its own field with a lunar cycle behind it. |
| How long should a weather spell last? | Currently 3 in-game hours (~7.5 real minutes). Pure playtest question; it is the knob most likely to be wrong. |
| Ladders are meant to be seven rungs | Only 2 of 9 discoveries have seven; the rest run 3–5. Either the target is wrong or the slice is under-authored. Decide before more regions are written against the shorter shape. |
| `lava_field` biome exists and nothing uses it | Author content for it, or drop it. |
| Which region gets the second field map? | The overworld has one map, so it has nothing to navigate. This is the first genuinely creative call rather than a structural one. |

---

## Deferred work

**`utils/check_playability.py`** — dropped for now at the user's direction, but three things are
known wrong:
- The `reach the last rung` line counts discoveries with ≥ 7 levels. Every discovery reaches its
  own last rung by definition, so the label describes something the code does not compute.
- A hardcoded `< 4` encodes "the actionable rung" as a constant, where the game treats it as
  whatever the ladder's length happens to be.
- The docstring promises that every rung's requirements can be satisfied *before* that rung.
  The code only checks set membership, so a cycle between two discoveries — each satisfiable
  "somewhere", neither ever first — would pass. This is the one real gap, and the only part
  worth building rather than deleting. Roughly 45 minutes.

**No helper for entering a gated sub-location.** `poi.subLocations[].requires` is authored and
the UI needs to check it; the brief tells the UI instance to ask for a tested helper in
`journey.ts` rather than inline the check.

**`origin/feature/canon-cleanup-and-design`** — 13 commits, unmerged, predates this work.

---

## Security

Two Hugging Face tokens were exposed during setup and must be treated as burned: one pasted
into chat, one printed unmasked by an inspection script I wrote. **Confirm both are revoked.**

`.gitignore:14` covers `.env.*`, verified, so `.env.local` is not tracked.
