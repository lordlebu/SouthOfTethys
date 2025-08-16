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
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sort_events(events):
    return sorted(events, key=lambda e: fantasy_date_key(e.get("date", "")))


def generate_mermaid(events):
    lines = ["```mermaid", "graph TD"]
    prev_id = None
    for idx, event in enumerate(events):
        node_id = f"E{idx}"
        label = f"{event.get('date', '')}: {event.get('title', '')}"
        lines.append(f'    {node_id}["{label}"]')
        if prev_id is not None:
            lines.append(f"    {prev_id} --> {node_id}")
        prev_id = node_id
    lines.append("```")
    mermaid_text = "\n".join(lines)
    return mermaid_text


def generate_markdown_summary(events):
    lines = ["# Timeline Summary\n"]
    for event in events:
        lines.append(f"## {event.get('date', '')}: {event.get('title', '')}")
        lines.append(f"**Summary:** {event.get('summary', '')}")
        chars = event.get("characters", [])
        if chars:
            lines.append(f"**Characters:** {', '.join(chars)}")
        else:
            lines.append(f"**Characters:** _None_")
        loc = event.get("location", None)
        if loc:
            lines.append(f"**Location:** {loc}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    timeline_path = "timeline/timeline.json"  # Correct path for Docker/CI
    mermaid_out_path = "timeline/timeline_mermaid.md"
    summary_out_path = "timeline/timeline_summary.md"
    timeline = load_timeline(timeline_path)
    # Handle both list and dict formats
    if isinstance(timeline, dict) and "events" in timeline:
        events = sort_events(timeline["events"])
    elif isinstance(timeline, list):
        events = sort_events(timeline)
    else:
        raise ValueError("timeline.json format not recognized")
    mermaid_graph = generate_mermaid(events)
    markdown_summary = generate_markdown_summary(events)

    # Write Mermaid diagram to file
    with open(mermaid_out_path, "w", encoding="utf-8") as f:
        f.write(mermaid_graph)

    # Write Markdown summary to file
    with open(summary_out_path, "w", encoding="utf-8") as f:
        f.write(markdown_summary)

    # Also print both to stdout for CI logs
    print("\n--- Mermaid Diagram ---\n")
    print(mermaid_graph)
    print("\n--- Timeline Summary ---\n")
    print(markdown_summary)
