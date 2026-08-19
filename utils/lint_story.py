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

The reference check is deliberately generic: any string matching a known id prefix is
treated as a reference, wherever it appears. That way a new field carrying entity ids is
covered the day it is added, rather than the day someone remembers to update this file.
"""

import json
import re
import sys
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
}

# folder -> schema stem, where the two differ.
SCHEMA_FOR = {
    "characters": "character", "events": "event", "fauna": "fauna", "flora": "flora",
    "field_maps": "field_map", "points_of_interest": "point_of_interest",
    "discoveries": "discovery", "field_questions": "field_question",
    "npcs": "npc", "vocabulary": "vocabulary", "regions": "region",
}

# Values that look like ids but are not entity references.
NOT_REFERENCES = {"sources", "type", "canon", "id"}

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
    try:
        from jsonschema import Draft7Validator

        validators = {}
        for folder, stem in SCHEMA_FOR.items():
            path = SCHEMA_DIR / f"{stem}.schema.json"
            if path.exists():
                validators[folder] = Draft7Validator(load(path))

        checked = 0
        for eid, (path, payload) in entities.items():
            v = validators.get(path.parent.name)
            if v is None:
                continue
            checked += 1
            for err in v.iter_errors(payload):
                errors.append(f"{path.parent.name}/{path.name}: {err.message[:110]}")
        schema_note = f"{checked} entities against {len(validators)} schemas"
    except ImportError:
        schema_note = "skipped (jsonschema not installed)"

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

    # --- every other reference ---------------------------------------------------
    known = set(entities)
    for eid, (path, payload) in entities.items():
        for ref in walk_refs(payload):
            if ref not in known:
                errors.append(f"{path.name}: reference '{ref}' does not exist")

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
