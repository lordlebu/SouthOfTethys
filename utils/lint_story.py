"""Validate database/ canon: index consistency and cross-refs."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database"
INDEX_PATH = DB / "index.json"

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
}


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def entity_path(entity_id: str) -> Path | None:
    for prefix, folder in PREFIX_DIRS.items():
        if entity_id.startswith(prefix):
            return DB / folder / f"{entity_id}.json"
    return None


def main() -> int:
    errors = []
    warnings = []

    if not INDEX_PATH.exists():
        print(f"❌ Missing {INDEX_PATH}")
        return 1

    index = load_json(INDEX_PATH)
    entities = index.get("entities", {})
    counts = index.get("counts", {})

    # Verify every listed ID has a file
    for category, ids in entities.items():
        for eid in ids:
            path = entity_path(eid)
            if path is None:
                # timeline epochs etc. may live under database/timeline/
                alt = DB / "timeline" / f"{eid}.json"
                if not alt.exists():
                    errors.append(f"Unknown ID prefix or missing file: {eid}")
                continue
            if not path.exists():
                errors.append(f"Missing file for {eid}: {path.relative_to(BASE)}")

    # Verify counts match list lengths
    for category, ids in entities.items():
        expected = counts.get(category)
        if expected is not None and expected != len(ids):
            errors.append(
                f"Count mismatch for {category}: index says {expected}, list has {len(ids)}"
            )

    # Cross-ref check on events
    events_dir = DB / "events"
    if events_dir.exists():
        for path in events_dir.glob("*.json"):
            ev = load_json(path)
            for field in ("participants", "predecessors", "successors", "artifacts"):
                for ref in ev.get(field) or []:
                    ref_path = entity_path(ref)
                    if ref_path and not ref_path.exists():
                        # location may be free-form or settlement id
                        warnings.append(f"{path.name}: dangling {field} ref '{ref}'")

    for w in warnings:
        print(f"⚠️  {w}")

    if errors:
        for e in errors:
            print(f"❌ {e}")
        print(f"\nLint failed: {len(errors)} error(s)")
        return 1

    print("✅ Lint passed: database/ index and files are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
