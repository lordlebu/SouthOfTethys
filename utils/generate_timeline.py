import pandas as pd
import re
import json
import os

def fantasy_date_key(date_str):
    # Parses "Act X, Scene Y" into sortable tuple (X, Y)
    match = re.match(r"Act (\d+), Scene (\d+)", date_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (9999, 9999)  # fallback for unsortable dates

def load_events(path):
    with open(str(path), encoding="utf-8") as f:
        data = json.load(f)
        # Support both list and dict formats
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("timeline.json format not recognized")

def build_timeline(events):
    character_data = {
        "name": "NewCharacter",
        "age": 20,
        "lineage": "HouseNew",
        "role": "NewRole",
        "traits": ["new_trait1", "new_trait2"]
    }

    events.append(character_data)

    return sorted(events, key=lambda e: fantasy_date_key(e.get("date", "")))

def summarize_timeline(timeline):
    for event in timeline:
        print(
            f"{event.get('date', '')}: {event.get('title', '')} - "
            f"{event.get('summary', '')}"
        )

if __name__ == "__main__":
    # Load the timeline data from JSON
    timeline_path = os.path.join(os.path.dirname(__file__), "utils/generate-timeline.py", "timeline/timeline.json")
    timeline_data = load_events(timeline_path)

    # Analyze the timeline data using pandas
    print("Before adding new character:")
    summary_stats = timeline_data.groupby(["date", "summary"]).mean()
    print(summary_stats)

    updated_timeline = build_timeline(timeline_data)
    summarize_timeline(updated_timeline)


