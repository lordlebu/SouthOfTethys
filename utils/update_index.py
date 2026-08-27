"""Rebuild `database/index.json` from what is on disk.

The manifest holds two things per category -- a list of ids and a count -- and `lint_story.py`
checks all three ways: every listed id has a file, every file is listed, and the count equals
the length of the *list*. Updating one without the others fails, and updating only `counts`
fails in a way that reads like the data is wrong rather than the manifest.

`database/AUTHORING.md` used to hand out a snippet that rebuilt `counts` from a glob and left
`entities` alone. That is exactly the wrong half: counts derived from disk while the id list
stayed stale, so the two disagreed and the lint blamed the entity. It also hid a real gap --
`places` had a count and no id list at all, which meant the both-directions check never ran on
it and 24 entities were never verified against the manifest at all.

    python utils/update_index.py               # rebuild, keeping the version
    python utils/update_index.py --bump minor  # ... and bump 1.13.0 -> 1.14.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database"
INDEX = DB / "index.json"

# Directories under database/ that are not entity folders.
NOT_ENTITIES = {"schemas", "timeline"}


def entity_folders() -> list[str]:
    return sorted(
        d.name for d in DB.iterdir()
        if d.is_dir() and d.name not in NOT_ENTITIES and any(d.glob("*.json"))
    )


def ids_in(folder: str) -> list[str]:
    """Ids in the folder, sorted -- the order the manifest has always used."""
    out = []
    for f in sorted((DB / folder).glob("*.json")):
        out.append(json.loads(f.read_text(encoding="utf-8")).get("id", f.stem))
    return sorted(out)


def bumped(version: str, part: str) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--bump", choices=("major", "minor", "patch"),
                    help="bump the manifest version as well")
    args = ap.parse_args()

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    before_ids = {c: list(v) for c, v in index.get("entities", {}).items()}

    entities, counts = {}, {}
    for folder in entity_folders():
        entities[folder] = ids_in(folder)
        counts[folder] = len(entities[folder])

    index["entities"] = entities
    index["counts"] = counts
    if args.bump:
        index["version"] = bumped(index["version"], args.bump)

    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    added = {c: sorted(set(entities[c]) - set(before_ids.get(c, []))) for c in entities}
    removed = {c: sorted(set(before_ids.get(c, [])) - set(entities[c])) for c in entities}
    for c in sorted(entities):
        for i in added[c]:
            print(f"  + {i}")
        for i in removed[c]:
            print(f"  - {i}")
    for c in sorted(set(before_ids) - set(entities)):
        print(f"  - whole category gone: {c}")

    print(f"\n{INDEX.relative_to(BASE)} → v{index['version']}, "
          f"{sum(counts.values())} entities across {len(counts)} folders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
