"""
Generate a Mermaid graph from timeline.json
for pictorial timeline visualization.
"""

import json
import re


def fantasy_date_key(date_str):
    # Parses "Act X, Scene Y" into sortable tuple (X, Y)
    match = re.match(r"Act (\d+), Scene (\d+)", date_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (9999, 9999)  # fallback for unsortable dates


def load_timeline(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sort_events(events):
    return sorted(events, key=lambda e: fantasy_date_key(e.get("date", "")))


def generate_mermaid(events):
    lines = ["```mermaid", "graph TD"]
    prev_id = None
    for idx, event in enumerate(events):
        node_id = f"E{idx}"
        label = (
            f"{event.get('date', '')}: {event.get('title', '')}"
        )
        lines.append(f'    {node_id}["{label}"]')
        if prev_id is not None:
            lines.append(f"    {prev_id} --> {node_id}")
        prev_id = node_id
    lines.append("```")
    mermaid_text = "\n".join(lines)
    return mermaid_text


if __name__ == "__main__":
    timeline_path = "timeline/timeline.json"  # Correct path for Docker/CI
    timeline = load_timeline(timeline_path)
    # Handle both list and dict formats
    if isinstance(timeline, dict) and "events" in timeline:
        events = sort_events(timeline["events"])
    elif isinstance(timeline, list):
        events = sort_events(timeline)
    else:
        raise ValueError("timeline.json format not recognized")
    mermaid_graph = generate_mermaid(events)
    print(mermaid_graph)
