import json
from pathlib import Path
import re


def fantasy_date_key(date_str):
    # Parses "Act X, Scene Y" into sortable tuple (X, Y)
    match = re.match(r"Act (\d+), Scene (\d+)", date_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (9999, 9999)  # fallback for unsortable dates


def load_events(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
        # Support both list and dict formats
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("timeline.json format not recognized")


def build_timeline(events):
    return sorted(events, key=lambda e: fantasy_date_key(e.get("date", "")))


def summarize_timeline(timeline):
    for event in timeline:
        print(
            f"{event.get('date', '')}: {event.get('title', '')} - "
            f"{event.get('summary', '')}"
        )


if __name__ == "__main__":
    # Build path relative to this script's location
    timeline_path = Path(__file__).parent.parent / "timeline" / "timeline.json"
    data = load_events(str(timeline_path))
    ordered = build_timeline(data)
    summarize_timeline(ordered)
