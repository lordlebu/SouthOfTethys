# Adding a story point

Everything canon holds is a **noun**. Pick the right one, write one JSON file, update the
manifest, run the gate. Four steps, and the gate tells you if you got it wrong.

If you only read one thing: **the folder you choose decides whether your writing reaches the
game.** Nine folders are exported into the browser bundle and eight are not, and putting a
hundred lore entries in an exported folder is the one mistake here with a cost attached.

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
| A ladder of understanding the player climbs | `discoveries/` | **yes** |
| A question the player forms a reading of | `field_questions/` | **yes** |
| An animal or a plant | `fauna/`, `flora/` | **yes** |
| A word in a constructed language | `vocabulary/` | **yes** |
| A god, a monster, a story people tell | `mythology/` | no |
| A group | `factions/` | no |
| An object that matters | `artifacts/` | no |
| A substance you can carry away | `materials/` | **yes** |
| An object a person can hold | `items/` | **yes** |
| A way of making | `processes/` | **yes** |
| A country-sized area | `regions/` | **yes** |

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

**`species` is a declared vocabulary too.** It answers what a person *is*, where `culture`
answers what they belong to, and both are checked. The twelve values live in
`database/species.json` with a gloss each; add one there in the same commit rather than typing a
thirteenth into a character and hoping. Four come in near-identical pairs on purpose --
`asura`/`asura_tainted`, `vanara`/`vanara_spirit` -- because the difference is what those stories
turn on.

### A material

A material answers what stuff *is* and where it comes from. It never answers how much of it
there is -- that is a question about one particular player, and it belongs to the game.

```json
{
  "id": "material_reed_fibre",
  "type": "material",
  "name": "Reed fibre",
  "classes": ["fibre"],
  "won_from": ["flora_saraswati_reed"],
  "found_in": ["wetland", "river"],
  "rarity": "common",
  "notes": "Retted in standing water until the pith rots away, then combed out.",
  "canon": "inferred",
  "sources": ["docs/bestiary.md"],
  "source_index": 0
}
```

**`classes` is a declared vocabulary**, in `database/material_classes.json`, and it is the
thing recipes actually name. A recipe asks for `#fibre` rather than for a list of species, so
canon can gain a new reed in ten years and every cordage recipe written today accepts it
without an edit. Give a material two classes where it honestly has two -- mahua seed is `oil`
and `produce` -- rather than picking the more important one.

**`won_from` may be absent.** Canon knows salt-crust is salt without owing anyone an account
of which pan it was scraped from. What it may *not* be is a bare string: like every other
reference in canon it names entities, and the walker checks them.

**This is not `flora.uses`.** That field stays where it is and answers a different question --
what people *do* with a plant, including `shade` and `navigational_landmark`, which are not
substances and cannot be carried. A material class says what you can take away.

### An item

An item is ordinary and repeatable. An `artifact` is a named thing canon treats as a character
in its own right, with a power and a cost -- the Mask of Tethys is an artifact, a reed rope is
an item, and there are thousands of the second.

```json
{
  "id": "item_reed_rope",
  "type": "item",
  "name": "Reed rope",
  "base_item": "item_cordage",
  "kind": "tool",
  "affords": ["bind"],
  "materials": ["material_reed_fibre"],
  "notes": "Light, cheap and rots. Everything that does not have to hold a boat.",
  "canon": "inferred",
  "sources": ["inferred from canon geography"],
  "source_index": 6
}
```

**`affords` is required and must have one entry.** An object that affords nothing is scenery,
and scenery belongs in a point of interest's description. The values are declared in
`database/affordances.json` and there is deliberately **no word for damage** -- a weapon `cut`s
and `deter`s. If combat is ever wanted it arrives by editing that file and recording the call in
`docs/decisions.md`, not by an item claiming it.

**`base_item` is inherit-then-override.** State what makes this one different and let the base
say the rest. The chain must terminate; a loop is a lint failure that names the path.

**Date anything bronze.** `epochs` absent means every epoch, which is right for a rope and
wrong for metal -- canon is a bronze world with iron as a rumour.

### A process

A process answers what a recipe has to be performed *at*, so a recipe can say "fired" without
restating what a kiln is.

```json
{
  "id": "process_firing",
  "type": "process",
  "name": "Firing",
  "performed_at": ["settlement"],
  "needs": ["burn"],
  "notes": "Clay to pottery in a kiln.",
  "canon": "inferred",
  "sources": ["inferred from canon geography"],
  "source_index": 7
}
```

**`performed_at` absent means anywhere, including standing in a field.** That is the honest
default -- somebody splitting reeds needs a river bank, not a building. Only name kinds where
the process genuinely needs the site.

**`needs` names an affordance, not a tool.** Firing needs something that burns, and canon should
not have to decide whether that is a hearth, a brazier or a pit. Any item affording it will do,
which is the same argument tag ingredients make about materials.

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

**Array order is load-bearing in exported folders.** The game picks species by indexing into
per-biome lists. `source_index` decides that order and anything without one sorts last. Adding
a species to `fauna/` or `flora/` shifts what lives on somebody's existing tile — so give new
species a `source_index`, and never re-sort an exported folder.

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
