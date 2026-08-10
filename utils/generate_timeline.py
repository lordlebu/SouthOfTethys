"""Build a merged timeline from database/events/*.json."""

import json
import sys
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
EVENTS_DIR = BASE / "database" / "events"
OUT_DIR = BASE / "timeline"
OUT_JSON = OUT_DIR / "timeline.json"
OUT_SUMMARY = OUT_DIR / "timeline_summary.md"


def load_events():
    events = []
    if not EVENTS_DIR.exists():
        return events
    for path in sorted(EVENTS_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            events.append(json.load(f))
    return events


def sort_key(ev):
    epoch_order = {
        "deep_antiquity": 0,
        "age_of_vanaras": 1,
        "migrations": 2,
        "civilization_dawn": 3,
        "current": 4,
        "post_cataclysm": 5,
    }
    return (epoch_order.get(ev.get("epoch") or "", 99), ev.get("id", ""))


def write_summary(events, path: Path):
    lines = ["# Timeline Summary\n", "_Generated from `database/events/`.\n"]
    for ev in events:
        title = ev.get("title") or ev.get("id")
        epoch = ev.get("epoch") or "unknown"
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
    events = sorted(load_events(), key=sort_key)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    write_summary(events, OUT_SUMMARY)
    print(f"✅ Wrote {len(events)} events → {OUT_JSON.relative_to(BASE)}")
    print(f"✅ Summary → {OUT_SUMMARY.relative_to(BASE)}")


if __name__ == "__main__":
    main()
