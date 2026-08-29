"""Validate database/ canon: schemas, the index, and every cross-reference.

This used to check that entities listed in index.json had files on disk, and warn about
dangling refs on events. It missed two whole classes of problem that had gone unnoticed for
a long time:

  * nothing validated entities against the schemas sitting next to them, so a schema could
    describe a shape nothing actually had;
  * nothing resolved references except on events, and only as warnings -- which is how all
    53 epoch references in canon came to point at ids that epochs.json does not declare,
    silently, while lint reported success.

So it now does three things, and treats all of them as errors:

  schema        every entity validates against its type's schema
  index         index.json and the files on disk agree, in both directions
  references    every id-shaped value resolves to something that exists
  clades        a subclade is one of *that* clade's sub-groups, and a growth form exists
  invariants    binomials, names and source_index are unique; every species has a binomial

The last two are here rather than in a schema because JSON Schema validates one document at a
time. It cannot say that two files disagree, which is how three species were entered twice and
two shared a name while lint reported success.

The reference check is deliberately generic: any string matching a known id prefix is
treated as a reference, wherever it appears. That way a new field carrying entity ids is
covered the day it is added, rather than the day someone remembers to update this file.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database"
INDEX_PATH = DB / "index.json"
SCHEMA_DIR = DB / "schemas"

# id prefix -> folder. Adding an entity type means adding a line here and a schema.
PREFIX_DIRS = {
    "character_": "characters",
    "event_": "events",
    "fauna_": "fauna",
    "flora_": "flora",
    "settlement_": "settlements",
    "region_": "regions",
    "artifact_": "artifacts",
    "faction_": "factions",
    "mythology_": "mythology",
    "field_map_": "field_maps",
    "poi_": "points_of_interest",
    "discovery_": "discoveries",
    "question_": "field_questions",
    "npc_": "npcs",
    "word_": "vocabulary",
    "place_": "places",
}

# folder -> schema stem, where the two differ.
SCHEMA_FOR = {
    "characters": "character", "events": "event", "fauna": "fauna", "flora": "flora",
    "field_maps": "field_map", "points_of_interest": "point_of_interest",
    "discoveries": "discovery", "field_questions": "field_question",
    "npcs": "npc", "vocabulary": "vocabulary", "regions": "region",
    "artifacts": "artifact", "factions": "faction", "mythology": "mythology",
    "settlements": "settlement",
    "places": "place",
}

# Values that look like ids but are not entity references.
NOT_REFERENCES = {"sources", "type", "canon", "id"}

# The three field maps the game's overworld screen is composed around.
#
# `src/content/overworldMap.ts` builds that entire screen out of these coordinates: where each
# node sits, the straight-line distances between maps, the viewBox fitted to their extent, and
# which way the outermost labels lean so they do not run off a phone. Moving one crashes
# nothing -- it silently rescales and re-lays-out the screen. Neither repository would catch
# it, because the geometry tests there check the arithmetic and not the data it runs on.
#
# So they are pinned here rather than only described in a plan. Canon may place new things
# anywhere it likes; these three are what everything else is placed relative to.
OVERWORLD_ANCHORS = {
    "field_map_lothal": {"x": 28, "y": 50},
    "field_map_dwarka": {"x": 16, "y": 64},
    "field_map_narmada": {"x": 58, "y": 20},
}

ID_SHAPED = re.compile("^(" + "|".join(re.escape(p) for p in PREFIX_DIRS) + ")[a-z0-9_]+$")


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def all_entities() -> dict[str, tuple[Path, dict]]:
    found = {}
    for folder in set(PREFIX_DIRS.values()):
        d = DB / folder
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            payload = load(f)
            found[payload.get("id", f.stem)] = (f, payload)
    return found


def walk_refs(node, key=None):
    """Yield every id-shaped string, skipping fields that are not references."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in NOT_REFERENCES:
                yield from walk_refs(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from walk_refs(v, key)
    elif isinstance(node, str) and ID_SHAPED.match(node):
        yield node


def main() -> int:
    errors: list[str] = []

    if not INDEX_PATH.exists():
        print(f"Missing {INDEX_PATH}")
        return 1

    entities = all_entities()

    # --- schemas -----------------------------------------------------------------
    #
    # A missing library is a failure, not a reason to skip.
    #
    # This block used to be wrapped in `except ImportError`, setting the note to
    # "skipped (jsonschema not installed)" and carrying on to report success. `requirements.txt`
    # did not list jsonschema, and `story-validation.yml` installs that file and nothing else --
    # so the only required check on `main` validated no schema, ever, while printing
    # "Lint passed: schemas, index and references are consistent."
    #
    # The lesson is the one the sibling repository keeps relearning: a check that silently
    # disables itself is worse than no check, because it also removes the pressure to write a
    # real one. Nobody reads a note in a green job.
    #
    # The import is deliberately outside any `try`. Catching ImportError around the whole block
    # would also swallow one raised by the validation code itself, which is how a narrow guard
    # becomes a wide one by accident.
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("Cannot validate schemas: jsonschema is not installed.")
        print("  pip install -r requirements.txt")
        print("")
        print("This is fatal rather than skipped on purpose -- see the comment in this file.")
        return 1

    validators = {}
    for folder, stem in SCHEMA_FOR.items():
        path = SCHEMA_DIR / f"{stem}.schema.json"
        if path.exists():
            validators[folder] = Draft7Validator(load(path))

    checked = 0
    unchecked: list[str] = []
    for eid, (path, payload) in entities.items():
        v = validators.get(path.parent.name)
        if v is None:
            unchecked.append(path.parent.name)
            continue
        checked += 1
        for err in v.iter_errors(payload):
            errors.append(f"{path.parent.name}/{path.name}: {err.message[:110]}")

    schema_note = f"{checked} entities against {len(validators)} schemas"
    if unchecked:
        # Not an error yet -- five folders have no schema at all, and writing them is its own
        # phase. But it should be visible in the output rather than inferred from a count that
        # does not match the entity total.
        tally = ", ".join(f"{n}\u00d7{f}" for f, n in sorted(Counter(unchecked).items()))
        schema_note += f" ({len(unchecked)} unchecked: {tally})"

    # --- index, both directions --------------------------------------------------
    index = load(INDEX_PATH)
    listed = index.get("entities", {})
    counts = index.get("counts", {})

    for category, ids in listed.items():
        folder = DB / category
        if not folder.exists():
            continue
        on_disk = {load(f).get("id", f.stem) for f in folder.glob("*.json")}
        for missing in sorted(set(ids) - on_disk):
            errors.append(f"index lists {missing}, no file on disk")
        for orphan in sorted(on_disk - set(ids)):
            errors.append(f"{category}/{orphan}.json exists but is not in index.json")
        if counts.get(category) is not None and counts[category] != len(ids):
            errors.append(f"count mismatch for {category}: index says {counts[category]}, list has {len(ids)}")

    # --- epochs ------------------------------------------------------------------
    epochs_path = DB / "timeline" / "epochs.json"
    declared = set()
    if epochs_path.exists():
        doc = load(epochs_path)
        declared = {e["id"] for e in (doc if isinstance(doc, list) else doc.get("epochs", []))}
    def epoch_values(payload):
        """Any field whose name mentions an epoch, not just `epoch` and `epochs`.

        Naming the two fields explicitly is what let `epoch_founded` sit unprefixed and
        unvalidated -- the same miss as the original bug, one field over.
        """
        for k, v in payload.items():
            if "epoch" not in k:
                continue
            for value in (v if isinstance(v, list) else [v]):
                if isinstance(value, str):
                    yield k, value

    for eid, (path, payload) in entities.items():
        for field, e in epoch_values(payload):
            if declared and e not in declared:
                errors.append(f"{path.name}: {field} '{e}' is not declared in timeline/epochs.json")

    # --- clades ------------------------------------------------------------------
    #
    # `clade` and `subclade` are two fields on one object whose legal values depend on each other,
    # and JSON Schema cannot say that: it can check each against a flat enum, which would let a
    # bird be a `dromaeosaurid`. The dependency lives here instead, with the other checks that need
    # to see more than one thing at a time.
    clades_path = DB / "clades.json"
    if clades_path.exists():
        tree = load(clades_path)["clades"]
        for eid, (path, payload) in entities.items():
            clade = payload.get("clade")
            sub = payload.get("subclade")
            if sub and not clade:
                errors.append(f"{path.name}: subclade '{sub}' without a clade")
            elif sub:
                allowed = (tree.get(clade) or {}).get("subclades") or {}
                if sub not in allowed:
                    names = ", ".join(sorted(allowed)) or "none"
                    errors.append(
                        f"{path.name}: '{sub}' is not a subclade of '{clade}' (allowed: {names})"
                    )

    # --- growth forms ---------------------------------------------------------------
    #
    # The plant half of the clade check. The schema pins the enum; this pins the *file* -- a form
    # can be added to growth_forms.json and forgotten in the schema, or the reverse, and then the
    # two disagree silently about what a plant is allowed to be.
    forms_path = DB / "growth_forms.json"
    if forms_path.exists():
        forms = set(load(forms_path)["forms"])
        for eid, (path, payload) in entities.items():
            form = payload.get("growth_form")
            if form and form not in forms:
                errors.append(f"{path.name}: '{form}' is not a growth form in growth_forms.json")

    # --- invariants across sibling files -------------------------------------------
    #
    # The checks JSON Schema structurally cannot make. It validates one document at a time, so it
    # can say a `scientific` is a string and never that two files carry the same one -- which is
    # exactly how three species came to be entered twice and pass a green lint for months.
    #
    # This is also the answer to "why not an off-the-shelf validator": every tool in that space
    # checks a file against a schema. Uniqueness across 256 siblings has to be written wherever it
    # lives, so it lives here, next to the loading that already happened.
    def unique(field, folders, label):
        seen: dict[str, str] = {}
        for eid, (path, payload) in entities.items():
            if path.parent.name not in folders:
                continue
            value = payload.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            key = value.strip().lower() if isinstance(value, str) else value
            first = seen.get(f"{path.parent.name}:{key}")
            if first:
                errors.append(f"{path.name}: {label} {value!r} is already used by {first}")
            else:
                seen[f"{path.parent.name}:{key}"] = path.name

    unique("scientific", {"fauna", "flora"}, "binomial")
    unique("source_index", {"fauna", "flora"}, "source_index")

    # A name is how a person refers to an entity, in a prompt, a note or a conversation. Two
    # entities answering to one name is a bug in the fiction before it is a bug in the data --
    # canon had two creatures both called "Lava-Vent Tubeworm", and the tool that applied clades
    # silently classified only one of them.
    #
    # **Within a folder, not across them.** The first version of this check was global and
    # immediately failed on `Dwarka` and `Lothal`, which are each a settlement *and* a field map --
    # the place and the walkable map of it, correctly sharing a name. A rule that forbids that is
    # describing a different world.
    names: dict[str, str] = {}
    for eid, (path, payload) in entities.items():
        name = (payload.get("name") or "").strip()
        if not name:
            continue
        key = f"{path.parent.name}:{name.lower()}"
        first = names.get(key)
        if first:
            errors.append(f"{path.name}: name {name!r} is already used by {first}")
        else:
            names[key] = path.name

    # Every species has to say what it is called in Latin, for the same reason it has to say what
    # clade it is: the alternative is the game guessing from a common name, and that guessing is
    # what this whole pass exists to end.
    for eid, (path, payload) in entities.items():
        if path.parent.name not in {"fauna", "flora"}:
            continue
        if not (payload.get("scientific") or "").strip():
            errors.append(f"{path.name}: no `scientific`")

    # --- the overworld's anchors ---------------------------------------------------
    for map_id, expected in sorted(OVERWORLD_ANCHORS.items()):
        entry = entities.get(map_id)
        if entry is None:
            errors.append(f"{map_id}: pinned as an overworld anchor but no longer exists")
            continue
        actual = entry[1].get("coordinates")
        if actual != expected:
            errors.append(
                f"{entry[0].name}: coordinates {actual} != the pinned {expected}. The game's "
                f"overworld screen is laid out from these; changing one silently rescales it. "
                f"If the move is deliberate, change OVERWORLD_ANCHORS in the same commit"
            )

    # --- somewhere-shaped fields point at somewhere ---------------------------------
    #
    # The reference check resolves anything matching a known id prefix. That is generic and
    # good, and it has one blind spot by construction: a bare string like `ironfang_mountains`
    # is not id-shaped, so `walk_refs` never yields it and nothing ever asks whether it exists.
    # Five event locations sat in canon that way -- looking exactly like references, invisible
    # to the check that resolves references, and unfixable until `place` gave them a home.
    #
    # So fields whose *name* says they point somewhere are resolved by name rather than by
    # shape. Two fields are deliberately absent. `origin` on a faction means ancestry as often
    # as geography -- `vedda_naga_hybrid` is a lineage. And `region` on a species holds a
    # bestiary slug rather than an id, by the design recorded in region.schema.json: the
    # bestiary was written first and its vocabulary is what the species carry. That one is
    # checked below, against the slugs regions actually declare.
    WHEREABOUTS = {"location", "field_map"}
    for eid, (path, payload) in sorted(entities.items()):
        for field in WHEREABOUTS:
            value = payload.get(field)
            if isinstance(value, str) and value and value not in entities:
                errors.append(
                    f"{path.name}: {field} '{value}' is not an entity. If it is a place canon "
                    f"has not modelled yet, add it under database/places/"
                )

    # A species' `region` is a `bestiary_region` slug, not an id. Unvalidated until now, which
    # is how a species could name a region that no region declares and read as placed.
    # Two of these are not geography, and are named here so the check catches a typo without
    # failing on a modelling question it cannot answer:
    #
    #   asura-conjurations  40 species grouped by what made them rather than where they live.
    #                       A coherent category; arguably it should be a faction or a tag
    #                       rather than a region, and that is a canon call.
    #   prototype-starters   6 ordinary animals -- a cloud antelope, a hill macaque, a monsoon
    #                       crane, a painted deer -- still carrying a development-era label.
    #                       These look like leftovers, but `region` is exported, so moving them
    #                       changes the game's bundle and is not a lint's decision to make.
    NON_GEOGRAPHIC = {"asura-conjurations", "prototype-starters"}
    slugs = {
        payload["bestiary_region"]
        for _eid, (_p, payload) in entities.items()
        if payload.get("type") == "region" and payload.get("bestiary_region")
    } | {"canon"} | NON_GEOGRAPHIC
    for eid, (path, payload) in sorted(entities.items()):
        if path.parent.name not in {"fauna", "flora"}:
            continue
        value = payload.get("region")
        if isinstance(value, str) and value and value not in slugs:
            errors.append(
                f"{path.name}: region '{value}' is not a `bestiary_region` any region declares"
            )

    # --- the authoring guide's templates are real ------------------------------------
    #
    # `database/AUTHORING.md` hands out copy-paste JSON, and its first version told authors to
    # write `"status": "living"` on a character -- not one of the four values the schema
    # allows, and precisely the mistake the guide exists to prevent. Four payloads in a
    # generated chapter failed on that same field the week it was written.
    #
    # A document that can drift from the schemas will. So the templates are checked against
    # them, and a template that stops being valid fails the build rather than teaching the
    # error to the next person. Only complete entities are checked -- the guide also shows
    # fragments, which have no `id` and are skipped.
    guide = BASE / "database" / "AUTHORING.md"
    if guide.exists() and validators:
        blocks = re.findall(r"```json\s*(\{.*?\})\s*```", guide.read_text(encoding="utf-8"), re.S)
        checked = 0
        for raw in blocks:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"AUTHORING.md: a template is not valid JSON -- {e}")
                continue
            if "id" not in payload or "type" not in payload:
                continue
            folder = PREFIX_DIRS.get(payload["id"].split("_")[0] + "_")
            v = validators.get(folder)
            if v is None:
                continue
            checked += 1
            for err in sorted(v.iter_errors(payload), key=lambda e: e.path):
                where = ".".join(str(x) for x in err.path) or "(root)"
                errors.append(f"AUTHORING.md: the {folder} template is invalid at {where} -- {err.message}")
        print(f"  templates  : {checked} in AUTHORING.md")

    # --- cultures are declared, not typed twice ---------------------------------------
    #
    # `culture` was 25 free-text values across 51 characters with nothing checking any of
    # them, which is how `asura` came to mean a culture, a species and a creature prefix at
    # once. Declared in `database/cultures.json` now, the way clades and growth forms are.
    cultures_path = DB / "cultures.json"
    if cultures_path.exists():
        known_cultures = {c["id"] for c in load(cultures_path).get("cultures", [])}
        for eid, (path, payload) in sorted(entities.items()):
            value = payload.get("culture")
            if isinstance(value, str) and value and value not in known_cultures:
                errors.append(
                    f"{path.name}: culture '{value}' is not declared in database/cultures.json"
                )

    # --- a derived creature names a real animal ---------------------------------------
    for eid, (path, payload) in sorted(entities.items()):
        base = payload.get("base_species")
        if not base:
            continue
        if base == eid:
            errors.append(f"{path.name}: base_species points at itself")
        elif base not in entities:
            errors.append(f"{path.name}: base_species '{base}' does not exist")

    # --- two events are not one event ------------------------------------------------
    #
    # The unique-name check above reads `name`, and an event carries `title`, so events were
    # never covered by it. A generated chapter arrived proposing `event_shadow_pact_saraswati`
    # titled "The Shadow Pact of Saraswati" while canon already held `event_shadow_pact` titled
    # "Shadow Pact of Saraswati" -- the same happening, the same two participants, a different
    # id and one extra article. Nothing would have caught it.
    #
    # Compared loosely on purpose: leading articles and case are not what makes two events
    # different.
    def loose(t: str) -> str:
        t = t.strip().lower()
        for article in ("the ", "a ", "an "):
            if t.startswith(article):
                t = t[len(article):]
        return t

    titles: dict[str, str] = {}
    for eid, (path, payload) in sorted(entities.items()):
        if payload.get("type") != "event":
            continue
        key = loose(payload.get("title") or "")
        if not key:
            continue
        first = titles.get(key)
        if first:
            errors.append(
                f"{path.name}: title {payload['title']!r} is already used by {first} -- two "
                f"events for one happening is a duplicate, not a cross-reference"
            )
        else:
            titles[key] = path.name

    # --- the sample fixture stays isolated -------------------------------------------
    #
    # The Dragon's Spine episode is kept deliberately as a test fixture: four entities across
    # four folders, one orphan event, the only mythology tied to an event. Useful to have, and
    # dangerous to leave unmarked -- somebody reading `database/` a year from now has no way to
    # tell a fixture from canon, and building on one quietly makes it load-bearing.
    #
    # `sample: true` says what it is. This says it stays that way: a sample may reference a
    # sample, and nothing else may reference one at all. That is the property that lets the
    # whole episode be deleted later with a four-file `git rm`, which is exactly what it was
    # kept for.
    samples = {
        eid for eid, (_p, payload) in entities.items() if payload.get("sample") is True
    }
    for eid, (path, payload) in sorted(entities.items()):
        if eid in samples:
            continue
        for ref in walk_refs(payload):
            if ref in samples:
                errors.append(
                    f"{path.name}: references '{ref}', which is a sample fixture. Canon must "
                    f"not depend on one -- the episode is kept so it can be deleted whole"
                )

    # --- events state their edges from both ends ------------------------------------
    #
    # `successors` and `predecessors` are two spellings of one edge, and only `successors` is
    # read when the timeline is drawn. So an edge declared on the predecessor side alone is
    # invisible -- it exists in canon and never appears in the picture, which is the worst of
    # both, because the data looks right to a reader and wrong to the renderer.
    #
    # Today the asymmetry runs the harmless way round: `event_founding_lothal` names the Black
    # Lotus Siege as a successor while the siege does not name it back, so the edge still draws.
    # Nothing guarantees the next one will lean the same way.
    for eid, (path, payload) in sorted(entities.items()):
        if payload.get("type") != "event":
            continue
        for succ in payload.get("successors") or []:
            other = entities.get(succ)
            if other and eid not in (other[1].get("predecessors") or []):
                errors.append(
                    f"{path.name}: names '{succ}' as a successor, but {succ} does not name "
                    f"'{eid}' as a predecessor"
                )
        for pred in payload.get("predecessors") or []:
            other = entities.get(pred)
            if other and eid not in (other[1].get("successors") or []):
                errors.append(
                    f"{path.name}: names '{pred}' as a predecessor, but {pred} does not name "
                    f"'{eid}' as a successor -- this edge would not be drawn"
                )

    # --- every other reference ---------------------------------------------------
    known = set(entities)
    for eid, (path, payload) in entities.items():
        for ref in walk_refs(payload):
            if ref not in known:
                errors.append(f"{path.name}: reference '{ref}' does not exist")

    # --- help nobody mentions ------------------------------------------------------
    #
    # `helps` is the whole of the "help people" system: a discovery names somebody whose life it
    # mends, and reaching the actionable rung is what mends it. But the field is only data. The
    # first solarpunk chain shipped with four discoveries naming three people and **not one line
    # from any of them acknowledging it** -- the camp's spring was turned around and nobody
    # mentioned it, which is why none of it landed when the game was played.
    #
    # So a discovery that says it helps somebody must be somebody's business to talk about.
    helped = {}
    for eid, (_p, payload) in entities.items():
        if payload.get("type") != "discovery":
            continue
        for who in payload.get("helps") or []:
            helped.setdefault(who, []).append(eid)

    for who, discoveries in sorted(helped.items()):
        person = entities.get(who)
        if person is None:
            continue
        prose = json.dumps(person[1].get("lines") or [])
        for did in discoveries:
            if did not in prose:
                errors.append(
                    f"{who}: {did} says it helps them, but they have no line requiring it -- "
                    f"help nobody mentions is a field in a file"
                )

    # --- names the player is not meant to reach -----------------------------------
    #
    # A discovery whose own notes say a thing "should stay unanswered" is a promise, and prose is
    # the one place nothing else checks. Canon knows who took the mask -- `event_tendua_crisis`
    # names Nila -- and a rung that says so would quietly close a thread the design wants left
    # open. This is cheap to break by accident and impossible to notice by reading a schema.
    #
    # Only rungs the player reads are checked. `notes` is for the canon reader and is where the
    # answer belongs.
    sealed = {
        eid: payload
        for eid, (_, payload) in entities.items()
        if payload.get("type") == "discovery" and "stay unanswered" in (payload.get("notes") or "")
    }
    if sealed:
        cast = set()
        for _eid, (_p, payload) in entities.items():
            if payload.get("type") == "character":
                cast.add(payload.get("name", ""))
                cast.update(payload.get("aliases") or [])
        cast = {n for n in cast if len(n) > 3}

        for eid, payload in sealed.items():
            prose = " ".join(l.get("entry", "") for l in payload.get("levels", []))
            for name in sorted(cast):
                if name in prose:
                    errors.append(
                        f"{eid}: rung prose names '{name}', but its notes say the answer "
                        f"should stay unanswered"
                    )

    print(f"  schema     : {schema_note}")
    print(f"  entities   : {len(entities)}")
    print(f"  epochs     : {len(declared)} declared")

    if errors:
        for e in errors[:40]:
            print(f"  FAIL  {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        print(f"\nLint failed: {len(errors)} error(s)")
        return 1

    print("\nLint passed: schemas, index and references are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
