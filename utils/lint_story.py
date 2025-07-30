import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TIMELINE_PATH = BASE_DIR / "timeline" / "timeline.json"
CHARACTER_DIR = BASE_DIR / "characters"
FLORA_PATH = BASE_DIR / "flora_fauna" / "species_tree.json"


def validate_date_format(date):
    return bool(re.match(r"Act \d+, Scene \d+", date))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    timeline = load_json(TIMELINE_PATH)
    species_data = load_json(FLORA_PATH)
    known_species = {s['species'] for s in species_data}  # Not used

    known_characters = set()
    for file in CHARACTER_DIR.glob("*.json"):
        with open(file) as f:
            c = json.load(f)
            if isinstance(c, dict) and "name" in c:
                known_characters.add(c["name"])
            elif isinstance(c, list):
                for entry in c:
                    if isinstance(entry, dict) and "name" in entry:
                        known_characters.add(entry["name"])

    ids = set()

    for event in timeline:
        # Check for ID duplicates
        if event['id'] in ids:
            print(f"❌ Duplicate event ID: {event['id']}")
            return 1
        ids.add(event['id'])

        # Check date format
        if not validate_date_format(event['date']):
            print(f"❌ Invalid date format: {event['date']}")
            return 1

        # Check character references
        for char in event.get("characters", []):
            if char not in known_characters:
                print(f"❌ Unknown character '{char}' in event {event['id']}")
                return 1

        # Check species references
        for species in event.get("species", []):
            if species not in known_species:
                print(f"❌ Unknown species '{species}' in event {event['id']}")
                return 1

    print("✅ Lint passed: All events are valid.")
    return 0


if __name__ == "__main__":
    exit(main())
