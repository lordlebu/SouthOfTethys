import json


def evolve_species(species_data, event):
    if event == "Climate Shift: Saraswati dries up":
        species_data["current_habitat"] = "Desert"
        species_data["evolution"].append(
            {"stage": "Desert Morph", "traits": ["Dune camouflage", "Thermal glide"]}
        )
    return species_data


# Example usage
with open("../flora_fauna/species_tree.json") as f:
    species = json.load(f)

updated = evolve_species(species[0], "Climate Shift: Saraswati dries up")

with open("../flora_fauna/species_tree.json", "w") as f:
    json.dump([updated], f, indent=2)
