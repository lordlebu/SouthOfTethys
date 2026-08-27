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

### Second round, after the game was played

Seven phases shipped and then somebody walked the map. Six things were wrong and not one was
visible to 460 tests, because a suite checks that things work rather than that they are worth
doing. These are the calls made in response.

**A field map declares its own landform.** Canon gained `relief` — `delta`, `island`, `plateau`,
`basin` — because one shaping rule cannot produce a harbour, an island and a plateau. It was
producing a dome on every map: elevation rose toward the centre, high ground classifies as hills
and forest at travel cost 2, and the average tile went from 1.15 at the rim to 1.98 in the middle.
Every map was hardest exactly where the walking happens.

Two constants in the engine's shapers are easy to get backwards and both were, at a cost of
several hours:

- *Raise the interior, never lower the rim.* They look equivalent — the difference is a constant
  and normalisation runs afterwards — but the sea threshold is a fixed fraction of the normalised
  range, so subtracting drags the world under water. Land went from 63–86% across twenty
  procedural seeds to 27–75%.
- *An easy middle means mid elevation and **low** moisture.* The only window yielding `plains`,
  the sole cheap non-coastal biome, is elevation 0.36–0.66 with moisture under 0.50. Raising
  moisture toward the middle — the intuitive way to make a delta feel like a delta — makes it more
  expensive, not less.

**Reachability is carved after placement, not shaped before it.** "The places are reachable
however far out they sit" cannot be a function of position, because placement happens later and
depends on the terrain. The engine eases the ground along the routes between placed points of
interest instead, so a valley is literally the path between two places rather than a landform one
happens to sit in. Narmada keeps cliffs in the middle because the line between the University and
the quarry is walkable through them.

**Dwarka was dried out: the sea left, not the land.** It was an island city; it is now a cold
desert around a dead harbour, with seawalls standing in dust and a market still opening on a tide
that stopped arriving. Six passes of engine tuning failed to make a wetland-dominant map walkable,
because wetland, forest and hills are all travel cost 2 and no shaping can invent cheap ground that
the palette does not contain. One lore change fixed it: travel cost went from 1.60 rising to 1.97
across the map, to a flat 1.10 falling to 1.06.

It cost five rewritten rungs across three chains and nothing else, because every discovery there
already read what water *did* rather than what it does. **When the engine keeps fighting the
content, the content may be the thing that is wrong.**

**The Dry Harbour was retired.** Four maps became three. It was a fourth variation on reading the
ground with no story in it, where the other three each carry one: Lothal the Mask Family, Dwarka
the Asura gate and the wrong-way skeleton, Narmada the University.

Nineteen entities, and checked rather than assumed to be safe — the only reference from anywhere
else in canon was Narmada listing it as a neighbour. The Glass Scar and Caravan Ground moved to
Dwarka, which is now the only map with desert in its palette, and both read better there: a seam
of fused sand pointing at a doorway things come through is a question, where the same seam in an
empty desert was a curiosity. Two rungs that dated themselves against the retired fossil channel
now date against the seawalls, which measure the same departure from the other side.

**The traveller carries a kit, not an inventory.** Bedroll, lamp, notebook and staff — fixed from
the start, never dropped, never spent. Consumables would open lamp oil, rope and dry tinder, which
is real resource pressure and also a survival game's spine; this one opens "Combat is absent by
design".

The bedroll answers a measured problem rather than a wanted feature: a full in-game day bought 23
steps of walking while the furthest tile from any shelter measured 72, so a traveller could be
three days from a roof through no fault of their own. That is not a hard choice, it is a trap. The
tile was rescaled so a day buys about eighty steps, and the bedroll covers the corners that are
still further than a day on rough ground.

Canon owns none of it and has no item concept at all — its only `artifacts` are the three story
masks. Canon says what exists in the world; the game says what the traveller brought.

**The mask thread reaches the event and never a name.** `discovery_chamber_below` gives Varuna a
sealed room under the tower, a shelf cut for the shape the stair niche also held, soot in a room
with no chimney, and mortar that dates it after the collapse. It does not give him a person, and
the last rung says so: *"I cannot say who, or when, or whether it was the same hands."*

Canon knows the answer — `event_tendua_crisis` names Nila, `event_mask_retrieval` names Asha,
iKnaya and Varna — and `discovery_mask_niche`'s own note says it *"should stay unanswered for a
long time; the diary needs entries the player cannot finish."* Rather than trust that,
`lint_story.py` now checks the rung prose of any discovery whose notes say "stay unanswered"
against canon's whole cast list. Prose is the one place nothing else looks.

**`helps` must be spoken.** A second new check refuses a discovery that names somebody in `helps`
when that person has no line requiring it. The first solarpunk chain shipped with four discoveries
naming three people and not one line acknowledging any of it — the camp's spring was turned around
and nobody mentioned it, which is exactly why none of it landed when the game was played. The
check found four more silent helps on its first run, on the other two maps.

---

### Third round, opening the lore layer (2026-08-27)

Canon is about to grow by hundreds of places across six epochs, almost none of which is meant
to ship. These are the calls that make that safe to do.

**The export boundary is a check now, not a convention.** `utils/check_export_boundary.py`
requires every folder under `database/` to be named in `BUNDLE` or in `NOT_EXPORTED`. A folder
in neither is an error, because the natural way to add a `place` type is to create the
directory and never think about the exporter again. It found one on its first run: `timeline`
had been withheld by omission rather than by decision -- the exporter's own comment claimed the
epoch table was excluded while the list did not mention it.

**Hashes, not `canon_version`.** The guard pins what the bundle hashes to, because the version
cannot do that job: `main` and `feat/flora-growth-forms` both declare `1.11.0` and produce a
different `species.json`, and it is the branch's copy that is committed in the game. A version
nobody bumps identifies nothing. Drift against the game repo is *reported and not fatal* --
canon does not own the game's working tree, and CI does not check it out.

**The three overworld coordinates are pinned in the linter.** `src/content/overworldMap.ts`
builds that whole screen out of Lothal (28, 50), Dwarka (16, 64) and Narmada (58, 20): node
positions, distances, the viewBox fitted to their extent, and which way the outermost labels
lean. Moving one crashes nothing -- it silently rescales the screen, and the geometry tests in
both repositories check the arithmetic rather than the data it runs on. Canon may place new
things anywhere; these three are what everything else is placed relative to.

**An event edge must be stated from both ends.** Only `successors` is read when the timeline is
drawn, so an edge declared on the predecessor side alone exists in canon and never appears in
the picture -- right to a reader, missing to the renderer. The one asymmetry in canon leaned the
harmless way and is now symmetric.

**Epoch order comes from the table, read at runtime.** Both generators carried a private copy
keyed on `"civilization_dawn"` while every event says `"epoch_civilization_dawn"`, so every
lookup missed, fell through to the `99` default, and alphabetical-by-id was the only sort that
ever ran. Both copies had also drifted from `epochs.json` in the same direction: each named an
`age_of_vanaras` that is not declared, and neither knew about `epoch_prehistoric`. Ordering now
lives once, in `canon_epochs`, because the bug *was* two copies that had drifted apart.

**Kahn's algorithm rather than networkx.** Twelve nodes do not justify a dependency, and the
cycle detection that would be the real reason to reach for one falls out of the algorithm
anyway. networkx is installed here only transitively; `story-validation.yml` installs
`requirements.txt` and nothing else, so using it would have meant adding it there.

**Mermaid for what stays small, SVG for what scales.** Six epochs and twelve events are
Mermaid's job. Geography is not: hundreds of places make a graph nothing can lay out and nobody
can read, and no styling fixes it. The map view, when it is built, is generated SVG over the
existing 0-100 grid -- no projection maths, diffable, dependency-free. Leaflet with
`CRS.Simple` is the upgrade path if pan and zoom over an illustrated basemap is ever wanted; it
exists for exactly this non-geographic case. `folium` never did: it wants real lat/lon.

**Generated artifacts are written straight into `docs/`, and `timeline/` is gone.** This one
had a mechanism nobody had found. CI regenerated the timeline on every push, and `docs/` stayed
stale anyway, because **`jekyll-gh-pages.yml` builds and deploys `./docs` exactly as committed
with no generation step**, while `ci.yml`'s `deploy-docs` regenerates first. Both target the
same `github-pages` environment, so whichever ran last won -- and half the time that was the
stale committed copy. Regenerating into a directory whose committed contents are also published
is a race, and it had been losing. One tracked location cannot drift from itself, and both
workflows now publish identical bytes in either order. `DESIGN.md`'s ruling is amended to match
rather than quietly contradicted.

**The cartography pipeline is deleted, not labelled.** `generate_map.py`, `cartography/` and
the published GeoJSON drew Jambhudweepa, the Himalayas, Saltbluff Plateau and Verdant Hollow --
a world canon does not contain. The previous entry below chose to list them as known-stale
rather than delete; that was right while a regeneration was plausible, and it is not: canon
states coordinates for three field maps on an abstract grid, and nothing correct can be
generated from that. Geography returns as canon entities first. `folium` left
`requirements.txt` with its only consumer.

---

## Open — needs a human call

| Question | Why it is open |
|---|---|
| Where does `full_moon` belong? | It is in the `weather` enum but is not weather. Probably its own field with a lunar cycle behind it. |
| How long should a weather spell last? | Currently 3 in-game hours (~7.5 real minutes). Pure playtest question; it is the knob most likely to be wrong. |
| Which way does `y` run on the 0-100 grid? | Canon has never said. The three pinned field-map coordinates fix those maps in place but imply no convention, and the reference drawing puts Dwarka north-west of Lothal while the grid values put it south-west if `y` increases downward. Settle it before any place is entered: the anchors make a later global flip impossible. |
| `place` as a new entity type, or a wider `settlement`? | Roughly ten named-but-unwalkable locations sit on the reference map, and the real number across the lore is in the hundreds. Whichever noun wins, its folder goes in `NOT_EXPORTED` in the commit that creates it. `point_of_interest` is the trap: it already carries `epochs` and looks right, and it ships to the game keyed to a walkable map. |
| What does an entity with no epoch default to? | Every era, or none. 363 of 494 entities carry no epoch, and 346 of those are fauna and flora, deliberately. The answer decides whether a Deep Antiquity atlas is crowded or bare. |
| How does a place change across epochs? | Recommended: identity and coordinates stated once, `epochs` for presence following the existing point-of-interest convention, and a per-epoch state block only on the few places that genuinely transform -- Dwarka harbour to drowned gate. One entity per place per epoch multiplies hundreds by six and makes "is this the same place?" unanswerable. |
| Which region gets the *third* field map? | Two exist and are joined (Lothal, the Narmada Plateau). A third is the first one with no structural argument behind it — it is a creative call. Candidates already in canon: Dwarka (the gates), the Shattered Sea, the Ganges Lava Sea (which would finally use `lava_field`). |

---

## Resolved

**The landmark loop stays** (decided 2026-08-13). The compass bearing to a great banyan and the
arrival page it ends in predate points of interest, and there are now two notions of arriving
somewhere. Retiring the older one was offered three times and declined: it is the shape the
original game had, it still works, and every one of its tests passes. Do not remove it as
tidying — it goes only if a design reason appears, not a consistency one.

**How much a field map costs, measured rather than guessed.** Across the four authored so far:
six points of interest each, six to nine discoveries running 31–50 rungs, one to three
questions, two or three people, and **1,450–2,200 words of prose** — about 1,700 on average,
plus roughly twenty JSON entities and their wiring.

The typing is not the constraint. Each map needs a *thesis* that is not a repeat of another's:
Lothal teaches looking, Narmada shows a record that begins at the wound, Dwarka is where the
locals are right, the Dry Harbour is out of date rather than mysterious. Finding five more of
those is the real work.

**And nine maps is not currently reachable.** Of the seven regions:

| Region | State |
|---|---|
| Saraswati Delta | two maps — Lothal, Dwarka |
| Narmada Plateau, Gedrosian Desert | one map each |
| Shattered Sea | **buildable** — `sea` and `forest` both render |
| Aravali | records no biomes at all; buildable once it does, as Gedrosian was |
| Ganges Lava Sea | buildable, but the ground renders as `mountains` until the `lava_field` tile exists |
| Tethys Sky Routes | **blocked** — `sky_island`, `sky_underside` and `open_sky` are not renderable |

So the realistic ceiling without new art is about seven maps, not nine, and one of those seven
would look wrong.

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

**The published map and timeline were stale placeholders — settled 2026-08-27.** The timeline
was regenerated and the map deleted; see the third round above. The judgement recorded here at
the time — list them as known-stale rather than delete, because a reader who follows a link to
fiction that contradicts canon is worse off than one told the artifact is not rebuilt yet — is
what eventually argued for deleting the map outright, once it was clear no regeneration could
replace it.

The estimate that the timeline was "a regeneration" was right about the data and wrong about
the cause. The generator had been producing correct canon on every push for months; a second
deploy workflow was publishing the committed copy over it.

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
