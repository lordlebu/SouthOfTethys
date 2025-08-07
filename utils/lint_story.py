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

    # Reorganize JSON data for easier access
    character_info = {}
    for file in CHARACTER_DIR.glob("*.json"):
        with open(file) as f:
            c = json.load(f)
            if isinstance(c, dict) and "name" in c:
                character_info[c["name"]] = {
                    "species": None,
                    "role": None
                }
            elif isinstance(c, list):
                for entry in c:
                    if isinstance(entry, dict) and "name" in entry:
                        character_info[entry["name"]] = {
                            "species": None,
                            "role": None
                        }

    location_data = {}
    for file in CHARACTER_DIR.glob("*.json"):
        with open(file) as f:
            c = json.load(f)
            if isinstance(c, dict) and "name" in c:
                location_data[c["name"]] = {
                    "regions": []
                }

    known_characters = set()
    for entry in character_info.values():
        known_characters.add(entry["name"])

    known_species = {s['species'] for s in species_data}  # Not used

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

        # Initialize character and species references
        characters = event.get("characters", {})
        species = event.get("species", {})

        # Populate character references
        for char_name, char_info in characters.items():
            if char_name in known_characters:
                char_info["species"] = species_data[char_name]["species"]
                char_info["role"] = location_data[char_name].get("regions", [])[0]
        # Populate species references
        for spec_name, spec_info in species.items():
            if spec_name in known_species:
                spec_info["evolution_chain"] = species_data[spec_name]["evolution_chain"]

        # Check character and species references
        for entry in character_info.values():
            if entry.get("species") is None or entry.get("role") is None:
                print(f"❌ Missing character information: {entry}")
                return 1

        for spec_name, spec_info in species.items():
            if spec_info.get("evolution_chain") is None:
                print(f"❌ Missing species information: {spec_name}")
                return 1

    print("✅ Lint passed: All events are valid.")
    return 0


if __name__ == "__main__":
    exit(main())
