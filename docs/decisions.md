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
| Where does `full_moon` belong? | It is in the `weather` enum but is not weather. Probably its own field with a lunar cycle behind it. |
| How long should a weather spell last? | Currently 3 in-game hours (~7.5 real minutes). Pure playtest question; it is the knob most likely to be wrong. |
| Which region gets the *third* field map? | Two exist and are joined (Lothal, the Narmada Plateau). A third is the first one with no structural argument behind it — it is a creative call. Candidates already in canon: Dwarka (the gates), the Shattered Sea, the Ganges Lava Sea (which would finally use `lava_field`). |

---

## Resolved

**Ladders are as long as they need to be** (decided 2026-08-12). An earlier note treated seven
rungs as a target and 3-of-18 as a shortfall. It is not one: a rung is one rewrite of a diary
entry, and a discovery gets as many as the understanding actually takes. The observed spread is
3–7, clustered at 4–5, and that is the shape, not a gap. Read the height from `lastRung()` and
never assume a fixed ladder.

**`climate` belongs to canon** (decided 2026-08-12). Weights live on the field map over the
four weathers the world actually produces; the schema refuses `flood` and `full_moon`. The
delta keeps the engine's old assumption, the plateau is mistier because the scarp holds cloud.
The engine's `DELTA_CLIMATE` is now only a fallback for a map that forgot to say.

**`lava_field` was declared and unused, and 40 species were mis-filed because of it.** The
Ganges Lava Sea is active volcanic rift cooling into jagged black basalt plains, and its fauna
are armoured, heat-resistant and often fused with volcanic minerals. The region now names
`lava_field`, and the 36 species that were filed under `mountains` name it too — kept alongside
`mountains` rather than replacing it, because `lava_field` is **not renderable yet**, and a
species with no renderable biome becomes `lore` and stops being placed at all. **Drawing it
needs a tile texture, which is the art instance's call.** Until then canon is accurate and the
engine simply filters it.

**`world.json` is no longer exported.** 46 KB of characters, events, settlements, factions,
artifacts, mythology and the epoch table that nothing imported. Vite inlines the bundle into
the page, so it was weight on every load. It returns when something reads it; a test asserts
the shipped set is exactly three files.

**The duplicated requirement semantics are accepted.** `holds` and `observed` exist in both
`src/journey.ts` and `utils/check_playability.py`. **Revisit only if a third consumer of these
rules appears** — at that point generating one from the other, or moving the check into the
game repo, starts to pay for itself. Until then the cost is two files to keep in step, and the
comment at the top of `check_playability.py` names the other one.

**`utils/check_playability.py` checked reachability, not order** — it asked "is this
requirement obtainable somewhere?", which passes a cycle: A's last rung needs B, B's last rung
needs A, both obtainable, neither ever first. That shipped, and the game's finishability test
caught it instead. Rewritten as a simulation that starts from nothing and does whatever
becomes possible until nothing more does; the two bogus rung-count constants are gone and the
summary now counts what actually finished. It is a CI gate in `story-validation.yml`, and it
duplicates two rules from the game's `src/journey.ts` — a real cost, accepted so canon can be
checked before export. Change the semantics in one, change them in both.

**Entering a gated sub-location** is now `canEnter` / `blockedFrom` in `src/journey.ts`.

## The retrieval service deploys itself

**Canon changes now rebuild and ship the index** (`.github/workflows/deploy-canon-service.yml`,
2026-08-13). It had drifted twice: the live service answered from a 420-chunk index for two
whole field maps while `/health` reported `ok: true` throughout — the index it had was healthy,
it was simply old, and nothing anywhere compared it to canon.

Three things about it that are easy to get wrong:

- **Production is a file upload from `dist-vercel/`, not a git build.** Vercel's own *Redeploy*
  button re-ships the stored snapshot, so it picks up changed environment variables and never
  picks up a new index. That is why the workflow runs the CLI.
- **The bundle carries no `.vercel` link**, so the project is named by `VERCEL_ORG_ID` and
  `VERCEL_PROJECT_ID` in the environment. Those are identifiers, not credentials; only
  `VERCEL_TOKEN` is secret.
- **The ONNX embedder is warmed before building.** chromadb hardcodes its model cache to the
  home directory and downloads 86MB on first use, which fails on a serverless filesystem — so
  the extracted model travels inside the bundle, and `build_deploy.py` refuses to run without
  a warm cache rather than shipping one that will 500 on its first request.

The last step asks the live `/health` whether its index covers canon, because a green deploy
with a stale index is precisely the failure this exists to prevent.

## Kept deliberately, not maintained

**The Hugging Face model `lordlebu/4000BCSaraswaty` is stock GPT-2 and nothing uses it**
(decided 2026-08-13: leave it, document it). It has not been updated in a year because the
approach was abandoned, not neglected — a 124M base model with no instruction tuning cannot
write to a brief, which is why the service moved to retrieval plus an instruction-tuned model
chosen by `CANON_LLM`.

Three things follow, and all three are easy to trip over:

- `model/README.md` is the card HF displays, and it used to claim "a custom causal language
  model for SouthOfTethys worldbuilding". It now says what the weights actually are. Editing
  anything under `model/` triggers `push-hf-model.yml`, so that correction reaches HF on merge.
- `vidur_portal/snippet_processor.py` has a path bug: `LOCAL_CONFIG` resolves *two* levels
  above the repo, so the local copy is never found and it downloads from the Hub instead. It
  does not matter today — the Hub copy is GPT-2 and the exception fallback is also `gpt2`, so
  every path ends at the same model — but it will mislead whoever reads it next.
- The GitHub Actions secret `HF_TOKEN` is a **write** token whose only consumer is that
  workflow. Nothing else needs write access; the service uses a separate inference-scoped token.

If the HF presence is ever worth something, publishing canon as a **dataset** is the version
with value in it — `dataset_card.md` and `dataset_infos.json` already exist unused.

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
