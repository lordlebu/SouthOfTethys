"""Build a merged timeline from database/events/*.json.

Event loading and ordering live in `canon_events`, shared with the Mermaid generator.
This file used to keep its own copy of the epoch order, keyed on ids canon does not
use, so it sorted alphabetically while reporting itself sorted by era.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canon_epochs import load_epochs
from canon_events import load_events, ordered

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
# Straight into docs/, which is what gets published and what a reader browsing the
# repository sees. There used to be a timeline/ build directory that CI copied across,
# and the copy is what went stale: docs/ held "Act 1, Scene 1: The Grove Fire" from a
# different project entirely while the generator had been producing real canon for months.
# One location cannot drift from itself.
OUT_DIR = BASE / "docs"
OUT_JSON = OUT_DIR / "timeline.json"
OUT_SUMMARY = OUT_DIR / "index.md"


def write_summary(events, path: Path):
    # An epoch's name rather than its id: this file is copied to `docs/index.md` and read by
    # people, and `epoch_civilization_dawn` is a key, not a era anybody calls it.
    named = {e["id"]: e.get("name") or e["id"] for e in load_epochs() if "id" in e}

    lines = ["# Timeline Summary\n", "_Generated from `database/events/`.\n"]
    for ev in events:
        title = ev.get("title") or ev.get("id")
        epoch = named.get(ev.get("epoch") or "", ev.get("epoch") or "unknown")
        lines.append(f"## {title}")
        lines.append(f"**Epoch:** {epoch}")
        if ev.get("summary"):
            lines.append(f"**Summary:** {ev['summary']}")
        parts = ev.get("participants") or []
        if parts:
            lines.append(f"**Participants:** {', '.join(parts)}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = ordered(load_events())
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    write_summary(events, OUT_SUMMARY)
    print(f"✅ Wrote {len(events)} events → {OUT_JSON.relative_to(BASE)}")
    print(f"✅ Summary → {OUT_SUMMARY.relative_to(BASE)}")


if __name__ == "__main__":
    main()
