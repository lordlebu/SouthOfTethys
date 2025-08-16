import json
import os

import folium


def load_json_file(path, required=True, geojson=False):
    if not os.path.exists(path):
        msg = (
            f"{'ERROR' if required else 'WARNING'}: File not found: {path}"
        )
        print(msg)
        if required:
            raise FileNotFoundError(msg)
        return None
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            msg = (
                f"{'ERROR' if required else 'WARNING'}: File is empty: {path}"
            )
            print(msg)
            if required:
                raise ValueError(msg)
            return None
        try:
            data = json.loads(content)
        except Exception as e:
            msg = (
                f"{'ERROR' if required else 'WARNING'}: Invalid JSON in {path}: {e}"
            )
            print(msg)
            if required:
                raise ValueError(msg)
            return None
        if geojson and (
            not isinstance(data, dict) or data.get("type") != "FeatureCollection"
        ):
            msg = (
                f"{'ERROR' if required else 'WARNING'}: {path} is not valid GeoJSON FeatureCollection."
            )
            print(msg)
            if required:
                raise ValueError(msg)
            return None
        return data


regions_geojson = load_json_file(
    "cartography/regions.geojson", required=False, geojson=True
)
overworld = load_json_file("cartography/overworld.json", required=False)

# Center map (customize as needed)
if isinstance(overworld, dict):
    map_center = [
        overworld.get("center_lat", 0),
        overworld.get("center_lon", 0)
    ]
else:
    map_center = [0, 0]
m = folium.Map(location=map_center, zoom_start=5)

# Add GeoJSON layer
if regions_geojson:
    folium.GeoJson(regions_geojson, name="Regions").add_to(m)
else:
    print("WARNING: No valid regions.geojson to display.")

# Optionally, add markers for key locations
if isinstance(overworld, dict) and "locations" in overworld:
    for loc in overworld["locations"]:
        if "lat" in loc and "lon" in loc:
            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=loc.get("name", "Unknown")
            ).add_to(m)

# Save to HTML
output_path = "cartography/interactive_map.html"
m.save(output_path)
print(
    f"Map saved to {output_path}"
)
