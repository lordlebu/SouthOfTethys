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
| Ladders are meant to be seven rungs | Only 3 of 18 have seven; the spread is 3–7, clustered at 4–5. Either the target is wrong or the slices are under-authored. Decide before another region is written against the shorter shape. |
| `lava_field` biome exists and nothing uses it | Author content for it, or drop it. |
| Which region gets the *third* field map? | Two exist and are joined (Lothal, the Narmada Plateau). A third is the first one with no structural argument behind it — it is a creative call. Candidates already in canon: Dwarka (the gates), the Shattered Sea, the Ganges Lava Sea (which would finally use `lava_field`). |

---

## Resolved

**`utils/check_playability.py` checked reachability, not order** — it asked "is this
requirement obtainable somewhere?", which passes a cycle: A's last rung needs B, B's last rung
needs A, both obtainable, neither ever first. That shipped, and the game's finishability test
caught it instead. Rewritten as a simulation that starts from nothing and does whatever
becomes possible until nothing more does; the two bogus rung-count constants are gone and the
summary now counts what actually finished. It is a CI gate in `story-validation.yml`, and it
duplicates two rules from the game's `src/journey.ts` — a real cost, accepted so canon can be
checked before export. Change the semantics in one, change them in both.

**Entering a gated sub-location** is now `canEnter` / `blockedFrom` in `src/journey.ts`.

## Deferred work

**`origin/feature/canon-cleanup-and-design`** — 13 commits, unmerged, predates this work.

**`world.json` is exported and imported by nothing** — 46 KB of characters, events,
settlements and factions shipped into the browser bundle for later phases. Correct for now,
but it is dead weight rather than something quietly in use, and `test/adapterCoverage.test.ts`
records that deliberately.

**`unlocks` on a vocabulary word is decorative.** `word_kia_uvai` claims it unlocks
`discovery_silver_water`, but that ladder's rung actually requires `word_kia_thal`. Nothing
enforces `unlocks`, so it drifts freely. Wire it to something or drop it.

---

## Security

Two Hugging Face tokens were exposed during setup and must be treated as burned: one pasted
into chat, one printed unmasked by an inspection script I wrote. **Confirm both are revoked.**

`.gitignore:14` covers `.env.*`, verified, so `.env.local` is not tracked.
