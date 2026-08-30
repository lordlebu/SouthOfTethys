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
is a race, and it had been losing. **The rest of that mechanism was found later the same day
and is recorded below: the two workflows did not merely race, they published different things,
and `ci.yml` no longer deploys at all.** One tracked location cannot drift from itself, and both
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
| Which region gets the *fourth* field map? | Three exist and are joined — Lothal, the Narmada Plateau and Dwarka, which answered the third. A fourth is a creative call with no structural argument behind it. The Shattered Sea is the only unbuilt region renderable today; the Ganges Lava Sea needs `lava_field` to get a tile first, and the Tethys Sky Routes need sky biomes. This question said *third* for long enough that Dwarka shipped while it still asked. |

**`species` is a declared vocabulary** (decided 2026-08-29, by the owner). Twelve values in
`database/species.json`, checked by lint, the same treatment `culture` got. Characters only:
fauna and flora answer "what is this" through `clade` and `base_species`, which is a different
question. The near-identical pairs -- `asura`/`asura_tainted`, `vanara`/`vanara_spirit` -- were
deliberately **not** merged. Declaring a vocabulary is about catching the thirteenth value typed
by accident, not about flattening twelve real distinctions into eight; collapsing a pair is an
authoring decision made on the characters.

**A drawn place must name its epochs** (decided 2026-08-29). `in_era` reads silence as "present
in every era", which is right for the 346 species relying on it and wrong for a city. All sixteen
placed places were silent, so all six atlas eras drew the same map with Harappa standing among
the Vanaras. `kind` now answers the question: ground takes all six eras, something people raised
begins when they raised it, and where canon dates a place canon wins over the rule of thumb. The
check asks only of a place actually drawn -- 22 places canon has not located may stay undated.

**The memory map is sliced per era, and a character may act outside their own** (decided
2026-08-29). It draws characters, the events of that era they were present at, and the factions
and cultures holding them; grouping is by faction where there is one and culture otherwise,
because Mermaid subgraphs cannot overlap and a person has both.

Two things came out of building it. **Membership is one-directional on purpose**: the faction
owns `members` and a character does not name one back, so the two cannot drift -- unlike the
event edges, which have no natural owner and therefore are mirrored. The plan had called the
missing reverse field a blocker; it is not one.

And **`epoch` on a character is when they first appear, not the only era they may act in.**
Filtering the map by dating alone drew the Post-Cataclysm as empty, while the Survival Train
happens there and its three participants are dated to the Current era and the Migrations. Varuna
walking into the era after the Shattering is the game's whole premise. A character is in an era
if canon dates them to it *or* they are present at something in it.

**The Prehistoric era gets no map** (decided 2026-08-29, by the owner: *"way too old"*).
`dump/Partial_map.png` shows a living Harappa and a standing university -- it is a picture of the
Civilization Dawn world, and the 0-100 grid traced off it describes that arrangement. The Age of
Vanaras predates every landmark the map is built from, so placing anything on it would claim a
geography canon does not have. The census still lists what the era holds; only the picture is
withheld. This is a stronger state than the Post-Cataclysm's, which still draws its points
because the three field-map anchors genuinely are cataclysm-shaped -- that era has lost its
coastline, not its arrangement.

**Guyuk is two lives** (decided 2026-08-29, by the owner). One character was a participant in
events four epochs apart: a teenage Tushara nomad in the Migrations, and a passenger on the
Survival Train after the Shattering. `character_guyuk` keeps the Migrations and Civilization
Dawn, and `character_guyuk_reborn` -- Guyuk the Seed-Gleaner -- carries the same seed-mind into
the Post-Cataclysm, linked by a new `reincarnation_of` field.

Deliberately **not** a key under `relations`, which is kinship. A rebirth is not a relative: the
Seed-Gleaner is not descended from the Storm-Bone Khan, she is her.

The document proposing this stated two reasons that are not true, and they are worth recording so
they are not re-derived. It said the overlap "fails the project's story-pathway and playability
compilers" -- `check_playability.py` passed before the change and after it. And it said it had
removed a forbidden `event_the_great_shattering` from the timeline; that event has never existed
in canon. The change is worth making on story grounds, which is the reason that survives: canon
should say whether it means one long life or two.

Only one event actually changed. The document also proposed re-creating three events canon
already holds -- one of them a duplicate of `event_naraka_portal` an article apart -- and two new
ids, `character_varuna_guardian` and `character_mitra_guardian`, for the Varuna and Mitra canon
already has. Varuna is the game's player character. That is the "Professor Onko" duplication a
second time.

**The Ammonite Man is a character** (decided 2026-08-29). He was `mythology_ammonite_man` and was
named as a participant in four events, which is not something a domain-and-aspect record does.
Moved to `character_ammonite_man`, six files repointed. This is the second time -- Owlman was the
first -- so the gate now refuses any event naming a `mythology_` id among its participants.

Credit where it is due: an outside reader (Gemini) spotted this. Its other two claims were wrong.
It reported both `event_fang_vs_scale_wars` and `event_asura_gondwana_intervention` as using
`myth_owlman`; both already used `character_owlman`, and the string `myth_` appears nowhere in
`database/`. And it asserted that the `mythology/` folder maps to a `myth_` prefix, citing
`myth_bhuta_kana_origin` as the correct form -- the mapping is `mythology_`, and that citation is
precisely the draft error corrected when the Jambenson book was ingested. It appears to have been
reading the drafts in `dump/` as though they were canon. The right conclusion for the wrong
reason is still worth acting on, but the reasoning did not survive checking.

**The Mask of Varkesh happens after Kavik dies** (decided 2026-08-29, by the owner). It was
ingested into Deep Antiquity off the draft, following the Shadow Pact. It belongs in Civilization
Dawn after `event_exile_of_shaashak`, which is what its own text was already saying: the
expedition reads the relic out of Kavik's stone tablets, and Shaashak only has those once he is
assassinated and she is exiled. The draft dated it and canon's own chronology disagreed; canon
was right.

**Kunti and Jambanson** (decided 2026-08-29). The conflict is real and is stated once, in
`dump/daedrasura-and-kunti-lore.md`: Shukradeva and Daedrasura weaponise her against the
Seedbearer to unpick his memory-seed work. It was captured as prose in her `notes`, which cannot
draw an edge, so she rendered orphaned. Now `event_kunti_against_jambanson`, running into the
Moon-Seed planting.

Worth recording: that document cites "The Mythic Legacy and Ritual Order of Jambenson" as a
source for her, and that book contains no mention of Kunti. Hers is a single-document character.

**Arin and Mira were never written into anything** (fixed 2026-08-29). Khadi's two daughters
carried kinship and a faction seat and appeared in no event, so the memory map drew them isolated.
They are in three of canon's events by its own prose: Arin clashes with Mehme in the market square
and Mira answers with prophecy, Arin questions Mehme's right to lead, Mira sails on the mask
expedition and stands at the tower summit holding the Mask of Tethys. Added to `event_stone_pact`,
`event_tendua_crisis` and `event_mask_retrieval`. Nila was missing from the Stone Pact for the same
reason and went in with them.

**Mira and Meera were already distinct** (checked 2026-08-29). Mira Starchild is Kia, Civilization
Dawn, Khadi's daughter; Meera of the Aravalis is Jharwa, the Migrations, sole survivor of the
massacre. They share no event, no culture and no epoch, and the document asking for the separation
proposed an Aravali event whose id was new and whose title, epoch and seven-person cast --
Vara-Ma, Orek and Thren included -- are what `event_aravali_massacre` already holds. Nothing to
separate; it was separate.

**The ekranoplan is canon, and has no crew** (added 2026-08-29). A rusted ground-effect craft
bought off delta salvagers at Vanga, flown at the Antarctic Ice Wall with a Vengi langur in the
cargo hold that finds the emergency fuel shut-off. Current era, between the Gondwana teleportation
and the Survival Train.

It is the **first event in canon with nobody in its cast**, and deliberately so: its source says a
nameless crew, and inventing three names to make a graph tidier is the wrong trade. It draws in the
timeline and not in the memory map, which is the honest outcome. The craft itself is
`place_ekranoplan`, `kind: vessel` -- the kind canon already keeps for the Kelpfang and the
Survival Train, somewhere that moves and is lived in.

**A place can inherit its position** (decided 2026-08-30). Canon names far more places than it
has ever surveyed: seventeen were named by events and drawn on no map, because only what was
legible on `Partial_map.png` ever got coordinates and everything authored since had none. Each
era's chapter mentioned ground its own map did not show.

`within` names what contains a place and the atlas resolves a position from the parent --
coordinates, or the middle of an outline -- **drawn hollow rather than filled**, so the map never
claims a precision canon does not have. One hop only: a chain would let an unplaced place borrow
from another unplaced place and land somewhere nobody chose.

Thirteen were given a parent canon actually supports. Five were not, and stay unplaced on purpose
-- `place_ancient_courts`, `place_gondwana`, `place_grassland_sanctuary`,
`place_ironfang_mountains` and `place_island_of_lund`. Guessing a container for those is
authoring geography, which is not the tooling's to do.

Switching inheritance on immediately reproduced the bug that produced the epochs rule: the Narmada
University Library appeared in Deep Antiquity, because `within` makes a place drawn and an undated
drawn place is in every era. The check now counts `within`, and reaches settlements as well as
places.

**Varuna is one being in two vessels** (decided 2026-08-30). Incorporating the Chess of Fate needed
the god to act, and `character_varuna` is species `deity_in_mortal_shell` -- "the ancient god of the
waters, bound during Epoch 5 to a mortal human frame". The captain *is* Varuṇa. So
`character_varuna_of_the_deep` holds the Prehistoric god and Captain Varuna carries
`reincarnation_of` back to him, exactly as Guyuk does.

`mythology_varuna` stays where it is. A mythology entity is the story told about someone, which is
what that folder is for; what it cannot be is a participant, and the gate refuses that now. The
myth points at the character instead.

**And so is Mitra** (2026-08-30). Giving Varuna a deity left Mitra half-modelled: also
`deity_in_mortal_shell`, also dated to the era the game is played in, and with no deity to be the
shell of. His own notes already called him "Varuna's divine partner". `character_mitra_of_the_oath`
holds that half -- Varuṇa keeps Ṛta by cold water and pressure, Mitra keeps it by agreement, which
is the same job done the opposite way.

The field's name is now doing two jobs and the schema says so. Guyuk the Seed-Gleaner is genuinely
reborn; Varuna and Mitra are **bound**, which is not the same thing. `deity_in_mortal_shell` is the
species that says a god is wearing a frame, and `reincarnation_of` is what says which god. Two of
the three uses are bindings, so reading the field name too literally would mislead.

**The explorer culture** (decided 2026-08-30, by the owner). Varuna, Rathak, Ruvan, Mitra and both
Guyuks. It is the one culture in canon that is not a people: every other entry names a lineage you
are born into, and this one names a way of moving through the world, which is why the same word
fits a Tushara nomad girl, a whale-blimp commander and a god in a mortal frame. Six holders across
four eras, the largest culture after `harappan`.

`narmada_survivor` was dropped -- invented for exactly one character who no longer holds it.
`tushara` and `trader` are kept with zero holders and a note each: they are real peoples named
across the prose, and a declaration is not a headcount.

**The front doors are checked, not remembered** (2026-08-30). `README.md` said v1.6.0 and 504
entities while the manifest said v1.26.0 and 588; `CLAUDE.md` said v1.13.0 and 517. Both are the
first thing a person or a model reads about this repository, and both had been wrong for weeks.
Nothing updates a number written in prose, and nobody notices a stale one because it looks like a
fact. The linter compares both against `index.json` now.

---

## Handover — the state at the end of the memory-map programme

Written 2026-08-30, closing the second programme. The first was *Drawing the Era Atlas*; this one
was *The Snippet Pipeline*.

**What exists.** Canon is 588 entities across 16 folders at v1.26.0. The book has four generated
views -- the timeline, the event graph, the atlas and the memory map -- each built from canon,
each sliced per era, each regenerated by a command in `CLAUDE.md` and by CI. `lint_story.py`
carries 38 checks; `check_playability.py` simulates a real playthrough; `check_export_boundary.py`
pins the game's bundle by hash.

**How a chapter gets in.** Put the document in `dump/` and run `ingest_draft.py` on that one file.
Nothing walks `dump/` on its own -- it is git-ignored and old documents are never reprocessed. The
checker catches nine error classes, and the drafts have produced every one of them repeatedly:
invented epoch ids, `myth_` for `mythology_`, a `status` outside the enum, undeclared cultures and
species, references to nothing, id collisions, duplicate event titles an article apart, honorific
duplicates of an existing person, and a `mythology_` id named as a participant.

**The habit that produced most of the value.** Five modelling errors this programme were invisible
in the JSON, passed lint and passed playability, and were found by looking at a drawing: six
identical era maps, an empty Post-Cataclysm, Guyuk standing in three eras, Manjalaya alone in a
pact her own summary says she was summoned into, and Khadi's daughters in no event at all. Each
became a lint rule. **Generate the view, look at it, then write the check** is the loop that
works here.

**What a next iteration should know.**

- *The drafts are confidently wrong about this repository.* Several arrived citing rules that do
  not exist -- that `mythology/` maps to a `myth_` prefix, that a chronological overlap fails the
  playability compiler, that a forbidden event needed removing which had never been authored.
  Three separate documents stated they were "schema-compliant with all cross-references
  resolving" and none was. Check the claim, never the assertion.
- *Prefer enriching to overwriting.* Four characters would have been replaced by partial redrafts
  that dropped canon fields. `ingest_draft.py` reports a collision; the right answer is usually to
  take the new prose into `notes` and keep everything else.
- *A place needs a position or a parent.* `within` exists so a chapter can name ground without
  inventing coordinates for it.
- *The game is a separate repository and a separate branch.* Never hand-edit its `data/canon/`.
  Re-export, then prove the per-biome pools are unchanged before trusting it -- array order is the
  seed contract, and the proof is cheap.

**What is deliberately unfinished** is in `database/TODO.md`: five unplaceable places, five
characters present at nothing, one castless event, and four events with no causal edge. None is a
defect. Each needs a ruling rather than a commit.

---

## Resolved

**The four geography and era rulings** (decided 2026-08-27). `y` increases southward, so the
screen convention wins and no renderer needs a flip; a named-but-unwalkable location is a new
`place` type rather than a stretched `settlement`; an entity with no epoch exists in *every*
era, because that is what fauna already meant; and a place states identity once with per-epoch
`states` only where it genuinely transforms. All four are written up in `DESIGN.md` as binding
rulings, with the reasoning and what each one rejected.

They were taken before a single place was entered. Every one of them is cheap now and expensive
after a hundred files exist, and the y-axis in particular cannot be revisited at all: the three
pinned field-map coordinates are load-bearing in the shipped game, so the convention had to be
fitted to them.

**Early eras get no map, and the atlas says so** (decided 2026-08-27). Five of six eras
render a timeline, an event graph and a census, and no map at all. The three field maps are the
only coordinates canon holds and their layout describes the world after the Collapse.

The argument that settled it was not about the grid. **The Cataclysm has not been worded yet** —
`epoch_post_cataclysm` is a single paragraph marked `status: authoring`, and no event sits in it.
Authoring pre-cataclysm coordinates would mean inventing the shape of the catastrophe in order to
place cities relative to it, and shipping nineteen positions that the fiction had never claimed.

Cheap to reverse, precisely because nothing has been entered against it — which is the opposite of
the y-axis ruling, and the reason this one could wait where that one could not.

**The Dragon's Spine episode is kept, and marked** (decided 2026-08-27). Four entities across
four folders — `event_dragon_spine`, `character_honan`, `mythology_gorvaxx`,
`place_ironfang_mountains` — were written to exercise the tooling rather than to tell the story.
They were very nearly deleted and are kept instead, because that spread is a genuinely useful
thing to test against: an orphan event, the only mythology tied to one, a character in an epoch
with almost nothing else in it, and a place derived from a bare location string.

Kept means marked. `sample: true` sits on the entity where a reader will see it, the linter
enforces that nothing outside the episode references it, and every generated view labels it. The
epoch note for Deep Antiquity, which used to narrate the forging in prose, no longer does — so
the whole thing still comes out with a four-file delete on the day it stops being useful.

The alternative was a `notes` convention, which nothing enforces. A fixture nobody can distinguish
from canon is how a test becomes load-bearing by accident.

**One workflow publishes the book, and it builds it** (decided 2026-08-27). `ci.yml` no longer
deploys Pages. It and `jekyll-gh-pages.yml` had been racing for the same `github-pages`
environment while publishing *different things*: the Jekyll workflow runs a real build over
`docs/`, and `ci.yml` called `upload-pages-artifact` on the directory with no build at all,
serving raw markdown and ignoring `_config.yml`, the nav and `_includes/`.

So the live site was a built site or a folder of `.md` files depending on which job finished
last. That is the deeper half of why the published book stayed stale while CI regenerated it on
every push — the earlier finding was that the stale copy sometimes won, and this is why it could
win at all.

**And Mermaid renders on the site now.** `docs/_includes/head-custom.html` loads it, which is the
hook `pages-themes/minimal` provides for exactly this. Five diagrams across the timeline and the
atlas had been publishing as source. It degrades to that same source if the CDN is unreachable,
which is the failure mode worth having.

It took two goes, and the first failure is the instructive one. The include targeted
`div.language-mermaid`, on the assumption that kramdown wraps a fence the way Rouge does — and
Rouge has no mermaid lexer, so kramdown falls through to a bare `<pre><code class="language-...">`
and emits no wrapper at all. The selector matched nothing, the diagrams kept publishing as code
blocks, and **from inside the repository that is indistinguishable from success**: the file is
there, the workflow is green, the page returns 200. Only fetching the built page and counting the
elements shows it. Both shapes are handled now, and the lesson is the one this project keeps
relearning — a check that cannot fail is not a check, and neither is a fix nobody looked at.

**The Great Shattering stays a mystery** (decided 2026-08-27). No `event_the_great_shattering`,
now or later. Canon keeps the consequences and withholds the account: the player works it out by
playing, dripped through `discoveries`, which is the mechanic the whole game is built on.

This reverses the recommendation that had been standing here. Writing the Shattering was being
called the keystone — the one authoring job that would unblock maps for five eras. It would also
have spent the central mystery of the era the game is set in, to gain a map. The trade is bad and
the withholding is the point.

It also settles the atlas ruling properly. Early eras get no map, and the reason is no longer
"nobody has written the *before* yet" — it is that the *before* is part of what the player is
meant to piece together. Nothing is pending; the page says so.

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
