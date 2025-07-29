import json
from pathlib import Path

def load_events(path):
    with open(path) as f:
        return json.load(f)

def build_timeline(events):
    return sorted(events, key=lambda e: e["date"])

def summarize_timeline(timeline):
    for event in timeline:
        print(f"{event['date']}: {event['title']} - {event['summary']}")

if __name__ == "__main__":
    data = load_events("../timeline/timeline.json")
    ordered = build_timeline(data)
    summarize_timeline(ordered)
