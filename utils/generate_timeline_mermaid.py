"""Generate Mermaid graph from database/events."""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EVENTS_DIR = BASE / "database" / "events"
OUT_DIR = BASE / "timeline"
OUT_MD = OUT_DIR / "timeline_mermaid.md"


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


def generate_mermaid(events):
    lines = ["```mermaid", "graph TD"]
    id_to_node = {}
    for idx, ev in enumerate(events):
        node = f"E{idx}"
        id_to_node[ev.get("id")] = node
        label = (ev.get("title") or ev.get("id") or "event").replace('"', "'")
        lines.append(f'    {node}["{label}"]')

    # Prefer explicit successor edges; fall back to sequential
    edged = set()
    for ev in events:
        src = id_to_node.get(ev.get("id"))
        for succ in ev.get("successors") or []:
            dst = id_to_node.get(succ)
            if src and dst:
                lines.append(f"    {src} --> {dst}")
                edged.add((src, dst))

    if not edged and len(events) > 1:
        for i in range(len(events) - 1):
            lines.append(f"    E{i} --> E{i + 1}")

    lines.append("```")
    return "\n".join(lines)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = sorted(load_events(), key=sort_key)
    mermaid = generate_mermaid(events)
    OUT_MD.write_text(mermaid + "\n", encoding="utf-8")
    print(f"✅ Mermaid → {OUT_MD.relative_to(BASE)} ({len(events)} events)")
    print(mermaid)


if __name__ == "__main__":
    main()
