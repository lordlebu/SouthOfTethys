# Adding a story point

Everything canon holds is a **noun**. Pick the right one, write one JSON file, update the
manifest, run the gate. Four steps, and the gate tells you if you got it wrong.

If you only read one thing: **the folder you choose decides whether your writing reaches the
game.** Twelve folders are exported into the browser bundle and nine are not, and putting a
hundred lore entries in an exported folder is the one mistake here with a cost attached.

**Making is not written here any more** (2 October 2026). Materials, items, processes, recipes,
vehicles and homesteads are the game's own data, in its `data/making/`. Canon gives the world its
context -- what lives where, who lives there, what they know and say -- and the game does its own
arithmetic. A line may still teach a recipe or ask for an item by its id, a field map may still list
its boat, and a custom may still name its dish: the game checks those ids exist.

---

## 1. Pick the noun

| You want to write | Use | Reaches the game? |
|---|---|---|
| Something that happened | `events/` | no |
| Somewhere named that a player will never stand in | `places/` | no |
| Somewhere people live, modelled in detail | `settlements/` | no |
| A walkable map | `field_maps/` | **yes** |
| A spot inside a walkable map | `points_of_interest/` | **yes** |
| A person in the history | `characters/` | no |
| A person the player can talk to | `npcs/` | **yes** |
| Something that happens to the player on a map | `happenings/` | **yes** |
| A line a people says on the road, shown in a cutscene | `sayings/` | **yes** |
| A person's arc, beat by beat: story cards, requests, a bond | `storylines/` | **yes** |
| A ladder of understanding the player climbs | `discoveries/` | **yes** |
| A question the player forms a reading of | `field_questions/` | **yes** |
| An animal or a plant | `fauna/`, `flora/` | **yes** |
| A word in a constructed language | `vocabulary/` | **yes** |
| A god, a monster, a story people tell | `mythology/` | no |
| A group | `factions/` | no |
| An object that matters | `artifacts/` | no |
| What a dish means | `foodways/` | no |
| A country-sized area | `regions/` | **yes** |
| Anything gathered, made, cooked, boarded or built | the game's `data/making/` | it *is* the game |

Two distinctions that are easy to get wrong:

**`place` vs `point_of_interest`.** A point of interest is *inside a field map* and the player
can walk to it — it needs a `field_map` and it ships. A place is anywhere else that has a name:
Harappa, the Deccan, the path to Lemuria. Hundreds of those are expected. `point_of_interest`
looks right for them because it already carries `epochs` and a description, and it is the wrong
answer.

**`character` vs `npc`.** A character is someone canon records. An NPC is someone standing on a
map with lines to say. Kavik is a character; the people in the Lothal camp are NPCs.

---

## 2. Write the file

One entity per file, named after its id, under the folder you picked. Ids are
`<prefix>_snake_case` and the prefix has to match the folder — `place_harappa` in `places/`.

**Every complete template below is validated against its schema by `lint_story.py`.** It has to
be: the first version of this file told you to write `"status": "living"`, which is not one of
the four values a character may have, and that is exactly the mistake it exists to prevent. A
guide that can drift from the schemas is a guide that will.

### An event

```json
{
  "id": "event_the_thing_that_happened",
  "type": "event",
  "title": "The Thing That Happened",
  "epoch": "epoch_civilization_dawn",
  "participants": ["character_kavik"],
  "location": "settlement_lothal",
  "predecessors": ["event_founding_lothal"],
  "successors": [],
  "causes": ["a_short_reason"],
  "outcomes": ["what_changed"],
  "summary": "One or two sentences. What happened, and to whom.",
  "canon": "primary",
  "sources": ["where this came from"]
}
```

`location` must be an entity — a settlement, a region, a field map or a place. A bare string
like `ironfang_mountains` used to be allowed and five of them accumulated; the linter now
rejects it.

**An edge must be stated from both ends.** If you name a successor, that event names you as a
predecessor. Only `successors` is read when the timeline is drawn, so an edge declared on one
side alone exists in canon and never appears in the picture.

### A place

A place is answered in four factors, and **the atlas needs all four**. Three of them were
optional until six eras drew the same map, with Harappa standing among the Vanaras because
nothing in the file said when it was built.

| Factor | Field | What happens if you leave it out |
|---|---|---|
| **What** it is | `kind` | Required already. |
| **Where** it is | `coordinates`, `extent` or `path` | It exists in the census but is never drawn. Honest and common — canon has not located everything. |
| **When** it is | `epochs` | *If you drew it:* it appears in all six eras, including ones before it existed. **This is now a lint failure.** |
| **How firmly** | `canon`, `sources` | It reads as established fact when it was traced off a picture. |

```json
{
  "id": "place_somewhere",
  "type": "place",
  "name": "Somewhere",
  "kind": "city",
  "epochs": ["epoch_migrations", "epoch_civilization_dawn", "epoch_current"],
  "continent": "mainland_asia",
  "coordinates": { "x": 29, "y": 15 },
  "description": "A sentence about what it is.",
  "notes": "What canon knows, what it does not, and where this came from.",
  "canon": "inferred",
  "sources": ["dump/Partial_map.png"]
}
```

**`kind` is one of a fixed list** — `continent`, `city`, `settlement`, `range`, `plateau`,
`plains`, `desert`, `coast`, `river`, `sea`, `island`, `forest`, `wetland`, `frontier`, `ruin`,
`route`, `vessel`, `unknown`. Coarse on purpose: the distinction that matters is a city from a
mountain range, not a city from a town.

**`kind` also answers `epochs`, nearly always.** Ground was here before anyone named it and is
here after they stop, so it takes all six eras: `continent`, `range`, `plateau`, `plains`,
`desert`, `coast`, `river`, `sea`, `island`, `forest`, `wetland`. Something people raised begins
when they raised it: `city`, `settlement`, `ruin`, `route`, `frontier`, `vessel`. That is why
Harappa, Mohenjodaro, Sihauli, the Northern Frontier and Vengi start at
`epoch_migrations` — people had to arrive before there was a city — while the Deccan and the
Nilgiri are on every map in the book.

Where canon *dates* a place, canon wins over the rule of thumb. Hyrcania is ground and gets all
six, but the two events that happen there sit in the Migrations, and if the steppe had been
named only in that era it would carry only that era.

**Four ways to say where.** A point is `coordinates`; an area is `extent`, a closed ring of
`[x, y]`; a river or a road is `path`, an ordered line read source-first. And when canon does not
know where something sits but does know what holds it, **`within`** names the parent and the atlas
takes the position from there, drawing it hollow instead of filled.

Prefer `within` to a guess. Seventeen places were named by events and drawn nowhere, because only
what was legible on the reference map ever got coordinates -- every era's chapter mentioned ground
its own map did not show. Saying the Nilgiri Canopy is in the Nilgiri is a fact canon already
holds; inventing a coordinate for it is not.

**Three ways to say where.** A point is `coordinates`; an area is `extent`, a closed ring of
`[x, y]`; a river or a road is `path`, an ordered line read source-first. A line is not a thin
ring — drawn as a ring it has to be traced out and back, and every edit has to keep both banks
in step.

**The grid is one world at one time.** `dump/Partial_map.png` shows a living Harappa and a
standing university, so it draws the world *before* the Great Shattering, and everything traced
off it is `"canon": "inferred"`. The three field-map anchors are not on that arrangement and are
not meant to be — they are cataclysm-shaped, which is the Shattering having happened in between
rather than an error in either. Do not reconcile them.

**Do not author `event_the_great_shattering`.** A generated chapter has already offered to, as
a predecessor for the Survival Train story. Canon keeps the Shattering's consequences and not
its account, on purpose: it is the mystery the game exists to arrive at, and it reaches the
player as a slow drip through `discoveries` rather than as a paragraph in `events`.

A place that changes across eras states its identity once and overrides only what changed:

```json
  "epochs": ["epoch_civilization_dawn", "epoch_current"],
  "states": [
    { "epoch": "epoch_post_cataclysm", "name": "The Drowned Gate", "status": "submerged" }
  ]
```

**So is `uses` on a plant.** Twenty-one values in `database/plant_uses.json`, and the thing to
get right is which question you are answering: a **material class** says what you can carry away
and a **use** says what the plant is for. More than half the uses are not substances at all --
nobody carries away shade, a boundary, or a tree they steer by. It was declared last, after it had
reached 51 free-text values across 27 plants with 44 of them used exactly once.

**`species` is a declared vocabulary too.** It answers what a person *is*, where `culture`
answers what they belong to, and both are checked. The twelve values live in
`database/species.json` with a gloss each; add one there in the same commit rather than typing a
thirteenth into a character and hoping. Four come in near-identical pairs on purpose --
`asura`/`asura_tainted`, `vanara`/`vanara_spirit` -- because the difference is what those stories
turn on.

### A foodway

A field map may still list the boat that is already there when the traveller arrives --
`"vehicles": ["vehicle_log_dugout"]` on Lothal. The vehicle itself is the game's; the game checks
the id and that the boat can float on the map.

A **foodway** is what a dish *means* -- whose it is, when it is eaten, what it marks -- and it
is **not exported**. The edible half is the game's item; this is a fact about the Harappans and
sits beside mythology. `occasion` is the load-bearing field: a dish with no occasion is a recipe,
and recipes are the game's.

```json
{
  "id": "foodway_flood_bread_rising",
  "type": "foodway",
  "name": "The rising loaf",
  "culture": "harappan",
  "dish": "item_flood_bread",
  "occasion": "The first day the river comes over the bank.",
  "meaning": "That the flood is a harvest and not a disaster.",
  "places": ["settlement_lothal"],
  "canon": "inferred",
  "sources": ["inferred from canon geography"],
  "source_index": 0
}
```

### A happening

```json
{
  "id": "happening_something_on_the_road",
  "type": "happening",
  "title": "Something on the road",
  "occasion": "road",
  "field_maps": ["field_map_narmada"],
  "requires": ["discovery_moving_spring"],
  "prose": "Second person, present tense, plain: what happens, as the card shows it.",
  "choices": [
    {
      "label": "A verb, in the traveller's register",
      "line": "What the diary records once it is taken.",
      "grants": ["word_maru_anu"]
    }
  ],
  "epochs": ["epoch_post_cataclysm"],
  "canon": "primary",
  "sources": ["where this came from"]
}
```

**Not an `event_`.** That prefix is the timeline: what happened in history. A happening is what can
happen to *one player* on a field map in the game's era -- a dream the delta has, somebody on the
road, what the camp is doing when you arrive. The game already weaves ordinary ones (tracks,
weather, road company) from whatever is on the tile; those never grant knowledge. A written one
**wins over a woven one whenever it can happen** and may grant exactly what a line may.

`occasion` is one of four: `night`, `arriving` (the first time you reach one of the points in
`at`), `road` or `working` (just after gathering). **Canon never says which day or how often** --
that is play, and the game owns it, as it owns how long `renews` takes.

`requires` is *observed*, not understood: a dream is built from what you have seen. And **every
choice must be takeable, and none worse than not having been here.** `check_playability.py` counts
every choice's `grants` as reachable once the map is walked and the requirements seen, refuses a
grant that is not a discovery, word, question or recipe, and refuses an `at` that is not on the
happening's own maps.

### A saying

```json
{
  "id": "saying_something_said_on_the_road",
  "type": "saying",
  "name": "Something said on the road",
  "text": "The words, exactly as said.\nA line break is a line break on screen.",
  "attribution": "Vedda saying",
  "carried_by": "vedda",
  "occasions": ["road", "fireside"],
  "field_maps": ["field_map_narmada"],
  "inspired_by": {
    "source": "Rigveda 10.75, the hymn that names the rivers",
    "note": "Original composition after Rigveda 10.75, the hymn that names the rivers. Not a translation, and not a quotation."
  },
  "notes": "What was changed from the draft to fit canon, if anything.",
  "epochs": ["epoch_post_cataclysm"],
  "canon": "primary",
  "sources": ["where this came from"]
}
```

What the peoples of South of Tethys say on the road -- at first light, at a ford, at the fire, on
arriving and on staying. The game shows them in its cutscenes; `occasions` says which (`opening`,
`dawn`, `departure`, `road`, `crossing`, `arrival`, `night`, `fireside`, `settling`) and
`field_maps`, when present, narrows them to a map. `carried_by` is a people from
`database/cultures.json`. **The sayings belong to the lore's various peoples** (the owner, 2 October
2026, reversing a misread of the day before that had given every one to the Vedda): the Vedda keep the
migration and ancestor lines and those written after Rigvedic hymns, and the rest are the Tushara's,
the Maru herders', the Kia's, the Harappans', the dune-scavengers', the Aravali glass-herbalists',
the Violet-Horned Clan's, the Sea-Drifters' and the Shaka-rauka's -- each where its line belongs. Canon never says when in a scene
a line appears, or how often it returns -- that is play.

Two rules, both the owner's of 1 October 2026:

**On screen, the credit is in-world only.** `attribution` is what the game shows -- "Vedda
saying", "Vedda waking-call" -- never a book, an author or a century. Where a line was written
after a real-world source, **`inspired_by` says so, and says it is an original composition after
that source, never a translation or a quotation.** The schema refuses a `note` that does not begin
"Original composition after". It is withheld from the game's bundle and shown by the lore portal.

**The line has to be true of this world.** No animal or people canon does not have -- a draft's
"wake the horses" became "wake the oxen", because Jambhudweep has no horse -- and ungendered unless
a named person is meant: "our mothers and fathers", "a traveller", "whoever knows". Record what was
changed from a draft in `notes`.

### Where a map is left from

Every field map with a neighbour names **`departs_from`**: the points of interest a traveller must
stand at to go on -- the cart yard, the pier, the caravan ground. The owner's ruling of 27 September:
maps are left from designated places, as a horse-cart leaves a yard and not a field. The first is
where somebody arriving is set down. `lint_story.py` refuses one that is not on its own map, and a
map with neighbours and none.

Where arriving and leaving are different places, say so with **`arrives_at`**: one point of
interest, on this map, where a traveller coming in is set down. The Aravali is left from its piers
but arrived at the Rail-Head, as its own `arrival` prose says. Absent means the first of
`departs_from`, which is right for any map whose cart yard is also where the carts come in.

**Every neighbour has a road, in the map's `roads`.** Each says what carries the traveller (`by`, a
vehicle), the painting (`art`, `journey-<a>-<b>` with the two maps in alphabetical order, so both
ends name one picture), two or three lines of what the way is like, and the `keeper` who sees you
off -- somebody found at one of the map's cart points, with one line. A road is stated from both
ends and both must agree on the vehicle. A happening with `occasion: journey` belongs to a road: its
`field_maps` are exactly the two ends. The game owns how long the crossing takes.

**A journey's opening is the map's `prologue`.** Only the map a journey begins on needs one -- today
Lothal. It is a saying shown alone (`opening`, which must list `opening` among its occasions) and up
to six plates, each a painting's file name (`prologue-1-road`), one or two lines in the second
person, and a saying. It says *you* and names nobody, and it shows the world as it is now: it never
states the Shattering. The game owns how long a plate stays and when the opening plays.

### A character

```json
{
  "id": "character_someone",
  "type": "character",
  "name": "Someone",
  "culture": "harappan",
  "species": "human",
  "status": "alive",
  "epoch": "epoch_civilization_dawn",
  "roles": ["what they do"],
  "notes": "Who they are, in a few sentences.",
  "canon": "primary",
  "sources": ["where this came from"]
}
```

---

**Does the same person appear four epochs apart?** `epoch` says when someone *first* appears,
not the only era they may act in, so one character standing in several eras is legal and often
right -- a guardian outlives an age. But a teenage steppe nomad walking into the era after the
Shattering is a different claim, and canon should say which it means. Write the later life as its
own character with `reincarnation_of` naming the earlier one. Two entities and a link says it;
one entity in five events across four eras does not.

**Somebody nobody wrote down gets a name from their people, not from you.** The game meets
strangers on the road -- carriers, drovers, pilgrims -- who are not characters and never will be.
Their names come from `given_names` on their culture in `database/cultures.json`, and only the
four peoples alive on the field maps in `epoch_post_cataclysm` carry a list: `harappan`, `kia`,
`maru`, and `asura_hybrid`, the Violet-Horned Clan who walk beside the Maru. To add a name, add it there, in that people's sound. The lint refuses one that is
already a word in any entity's name, or that two peoples share -- so a given name can never turn
out to be somebody who already exists. Names are ungendered, as canon's own people's are.

**If it acts, it is a character.** A `mythology_` entity holds a name, a domain and an aspect --
it is a story told, not somebody who was there. The moment it negotiates, travels or is named a
participant, it belongs in `characters/`. This has happened twice, to Owlman and to the Ammonite
Man, and both times an outside reader noticed before the gate did. The gate checks it now.

## 3. Update the manifest

```bash
python utils/update_index.py --bump minor
```

`index.json` holds **two** things per category — a list of ids and a count — and
`lint_story.py` checks all three ways: every listed id has a file, every file is listed, and the
count equals the length of the *list*. Rebuild it with the script rather than by hand.

This section used to hand out a snippet that rebuilt `counts` from a glob and left `entities`
alone, which is the wrong half: the counts came from disk while the id list stayed stale, so the
two disagreed and the lint blamed the entity you had just written. It also hid a real gap —
`places` had a count and no id list at all, so the both-directions check never ran on it and 24
entities went unverified against the manifest.

## Drafting a whole chapter at once

If a chapter arrives as one document -- prose with JSON blocks in it, which is how every
chapter so far has arrived -- check it before writing anything:

```bash
python utils/ingest_draft.py dump/my-chapter.md
python utils/ingest_draft.py dump/my-chapter.md --apply    # writes, if clean
```

It reads every fenced JSON block and reports per entity: schema errors, id collisions with
canon, epochs that are not declared, references to things that do not exist, cultures that are
not declared, event titles that duplicate one canon already has, and successor edges that run
backwards through time. `--apply` refuses while anything is wrong.

**Every check in it is one that a real chapter got wrong.** Four arrived already structured and
already broken, and three of the four stated they were schema-compliant with all references
resolving. The tool exists because reading the claim is not the same as checking it.

## 4. Run the gate

```bash
python utils/lint_story.py             # schemas, the index, every reference
python utils/check_playability.py      # can a player actually reach it
python utils/check_export_boundary.py  # can it reach the game by accident
```

All three run in CI and all three must pass. Then regenerate what reads canon:

```bash
python utils/generate_timeline.py
python utils/generate_timeline_mermaid.py
python utils/generate_atlas.py
```

`docs/` is tracked, so commit what those write. It is the published book, and tracking it is
what makes a stale one visible in a diff rather than only on the live site.

---

## Things that will bite

**Bumping the version moves every bundle hash.** `canon_version` is embedded in each exported
file, so a version bump alone fails `check_export_boundary`. That is correct. Re-pin
deliberately, in the same commit:

```bash
python utils/check_export_boundary.py --update
```

**A failure there is usually right.** It means something you wrote reached the game's data. If
that was the intent, re-pin. If it was not, you probably put an entity in an exported folder.

**`source_index` is required on every species — but array order is no longer load-bearing.**
Take the next free number and never re-sort a folder.

The history is worth keeping, because the rule survived its reason. The game used to pick species
by *indexing into* per-biome lists, so the order they arrived in decided what grew on a given
tile. The field was called optional — "anything without one sorts last" — which was true and was
not enough: unindexed entries sort last *by id*, so adding `flora_ashwagandha` put it ahead of
`flora_asura_thorn` and moved every unindexed species after it. Twenty-five plants arrived across
two batches and quietly rearranged what was growing on saved ground.

The game now picks species by **rendezvous hashing over their ids** rather than by position, so a
species' tiles depend on nothing but that species and that tile. Adding one to canon takes only
the tiles it wins outright — measured at 4.8% of a biome's ground, against 95.4% under the old
scheme. **Adding canon content is no longer a save-breaking change on the game side.**

The index stays required, for two reasons that have nothing to do with the seed: it is the
authored bestiary sequence the books read in, and a required unique field is a cheap guard against
accidental duplicates. It is presentation now, not a contract.

**A new folder must be classified.** If you add an entity type, name its folder in `BUNDLE` or
`NOT_EXPORTED` in `utils/export_canon_bundle.py`, and in `DB_FOLDERS` in
`services/chroma/index_chroma_service.py`, in the same commit. Three hardcoded lists, all
checked; a folder in none of them fails the gate on purpose.

**Do not put example JSON in a folder under `database/`.** Anything matching `database/*/*.json`
is canon as far as the tooling is concerned, and a `templates/` folder would fail the boundary
check. That is why the templates above are inline in this file.

**No epoch means every era — and for a place you drew, that is now an error.** Silence reads
as timeless rather than unplaced, which is deliberate and is what fauna has always meant: a
crocodile does not belong to an era. It is wrong for a city. So the rule is split. A place
carrying `coordinates`, an `extent` or a `path` **must** name its `epochs`; everything else may
stay silent. That narrowness is the point — canon has 22 places it has not located, and dating
them is not the price of drawing a map.

**Writing a fixture rather than a story point?** Mark it `"sample": true`. Nothing that is not
itself a sample may reference it, so it stays deletable.

---

## Where the reasoning lives

| File | What it holds |
|---|---|
| `DESIGN.md` | the binding rulings — the era, the grid, what a place is |
| `docs/decisions.md` | every call made on the project's behalf, and what is still open |
| `database/VALIDATION.md` | what the linters check, and what they deliberately do not |
| `database/TODO.md` | what is missing |


## Storylines

A person's arc is a `storylines/` entity: an ordered run of beats on one map, each a story card that
comes when its moment does and the beat before it is done. A beat is `when` it can come (`arriving`
at a place on the map, a `night` slept there, or a step on the `road`), what it `requires` the
traveller to hold, what it `asks` them to hand over (the beat waits until it is all carried, and the
first choice gives it), the painting (`art`), the prose and the choices. A storyline that `joins`
ends on a beat that `joins`: from then on the person walks with the traveller and can be walked as.

The arcs of 2 October 2026 are the owner's: Guyuk, the Seed-Gleaner of the Aravali, who joins, and
the Asura princess of the Narmada, who forms the bond and stays back for her people. The prose is
drafted to the owner's outline for the owner to rewrite. A person met only through her arc -- Guyuk
-- is an NPC with no `found_at`. So is somebody met only on the craft they drive: `drives` names the game's
`vehicle_`, and Sudama drives the Sinauli wagon round Dwarka's Caravan Ground for Jarro.


## Fireside stories

A `night` happening with `camps` belongs to a kind of camp -- `adventurers`, `dacoits`, `pilgrims` or
`drovers` -- and happens on a night slept beside one: a story told at somebody else's fire. Two per
kind to start (2 October 2026). The game prefers a written one it has not told before, and falls back
to its own woven fireside when they are all told.
