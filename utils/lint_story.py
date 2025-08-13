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

def generate_timeline_data(timeline_path, character_dir, flora_path):
    timeline_data = load_json(timeline_path)
    species_data = load_json(flora_path)

    # Reorganize JSON data for easier access
    character_info = {}
    for file in character_dir.glob("*.json"):
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
    for file in character_dir.glob("*.json"):
        with open(file) as f:
            c = json.load(f)
            if isinstance(c, dict) and "name" in c:
                location_data[c["name"]] = {
                    "regions": []
                }

    known_characters = set()
    ids = set()

    for event in timeline_data:
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
        if characters:
            species_data_entry = species_data.get(characters[0], {})
        else:
            print("❌ Missing character data: Characters list is empty")
            return 1

        species = {k: v for k, v in species_data_entry.items() if k in event}
        for char_name in character_info:
            if isinstance(character_info[char_name], dict):
                char_info[char_name]["species"] = species_data.get(char_name, {}).get("species")
                char_info[char_name]["role"] = location_data.get(char_name, {}).get("regions", [])[0]
        # Populate species references
        for spec_name in species:
            if spec_name in species_data:
                species[spec_name]["evolution_chain"] = species_data[spec_name].get("evolution_chain")

        # Check character and species references
        for char_info in character_info.values():
            if "species" not in char_info or "role" not in char_info:
                print(f"❌ Missing character information: {char_info['name']}")
                return 1

    print("✅ Lint passed: All events are valid.")
    return 0

if __name__ == "__main__":
    exit(generate_timeline_data(TIMELINE_PATH, CHARACTER_DIR, FLORA_PATH))
