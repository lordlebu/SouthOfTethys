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

character_list = []

# Create a new character
character_data = {
    "name": "Elia of Akaran",
    "age": 26,
    "lineage": "House Akaran",
    "role": "Herbalist",
    "traits": ["empathetic", "resilient", "keen-sense-of-smell"]
}

# Add the new character to the list of characters
character_list.append(character_data)


# Load existing characters from files
character_info = {}
location_data = {}
for file in BASE_DIR.glob("characters/*.json"):
    with open(file) as f:
        c = json.load(f)
        if isinstance(c, dict):
            character_info[c["name"]] = {
                "species": None,
                "role": None
            }
            location_data[c["name"]] = {
                "regions": []
            }
        elif isinstance(c, list):
            for char in c:
                if isinstance(char, dict) and "name" in char:
                    character_info[char["name"]] = {
                        "species": None,
                        "role": None
                    }
                    location_data[char["name"]] = {
                        "regions": []
                    }

known_characters = set()
ids = set()

for event in load_json(TIMELINE_PATH):
    # Check for ID duplicates
    if event['id'] in ids:
        print(f"❌ Duplicate event ID: {event['id']}")
        exit(1)
    ids.add(event['id'])

    # Check date format
    if not validate_date_format(event['date']):
        print(f"❌ Invalid date format: {event['date']}")
        exit(1)

    # Initialize character and species references
    characters = event.get("characters", [])
    if isinstance(characters, list) and len(characters) > 0:
        flora_data = load_json(FLORA_PATH)
        char_species_name = characters[0]
        if isinstance(flora_data, dict):
            species_data_entry = flora_data.get(char_species_name, {})
        elif isinstance(flora_data, list):
            # Search for species dict with matching name
            species_data_entry = next((item for item in flora_data if isinstance(item, dict) and item.get("name") == char_species_name), {})
        else:
            species_data_entry = {}
    else:
        print(f"⚠️ Warning: Missing character data in event '{event.get('id', 'unknown')}': Characters list is empty or not a list")
        continue

    species = {k: v for k, v in species_data_entry.items() if k in event}
    flora_data = load_json(FLORA_PATH)
    for char_name in character_info:
        if isinstance(character_info[char_name], dict):
            # Species assignment
            if isinstance(flora_data, dict):
                character_info[char_name]["species"] = flora_data.get(char_name, {}).get("species")
            elif isinstance(flora_data, list):
                species_obj = next((item for item in flora_data if isinstance(item, dict) and item.get("name") == char_name), {})
                character_info[char_name]["species"] = species_obj.get("species")
            else:
                character_info[char_name]["species"] = None
            # Location assignment
            regions = location_data.get(char_name, {}).get("regions", [])
            if regions:
                character_info[char_name]["role"] = regions[0]
            else:
                print(f"⚠️ Warning: Missing location info for character '{char_name}'")
                character_info[char_name]["role"] = None
    # Populate species references
    for spec_name in species:
        flora_data_for_species = load_json(FLORA_PATH)
        if isinstance(flora_data_for_species, dict) and spec_name in flora_data_for_species:
            species[spec_name]["evolution_chain"] = flora_data_for_species[spec_name].get("evolution_chain")
        elif isinstance(flora_data_for_species, list):
            species_obj = next((item for item in flora_data_for_species if isinstance(item, dict) and item.get("name") == spec_name), {})
            if "evolution_chain" in species_obj:
                species[spec_name]["evolution_chain"] = species_obj["evolution_chain"]

    # Check character and species references
    for name, char_info in character_info.items():
        if "species" not in char_info or char_info["species"] is None:
            print(f"⚠️ Warning: Missing species information for character '{name}'")
        if "role" not in char_info or char_info["role"] is None:
            print(f"⚠️ Warning: Missing location/role information for character '{name}'")

print("✅ Lint passed: All events are valid.")
exit(0)
