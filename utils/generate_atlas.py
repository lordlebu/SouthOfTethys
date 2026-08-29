"""Draw canon as it stood in one era, or in all six.

The atlas answers a question the other generators cannot: *what existed then?* The timeline
says when things happened and the event graph says what caused what, but neither tells you
that the Aranta was wilderness in every era while Dwarka was a harbour and then a drowned
gate.

Three views per era, and they deliberately do not share a renderer:

  census   what canon holds in that era, split into things dated to it and things that
           carry no epoch at all. That split matters more than the totals: 363 of 513
           entities name no epoch, and under the ruling in DESIGN.md they exist in every
           era. Showing 256 fauna in Deep Antiquity and calling it a finding would be
           noise; showing them as *timeless* is the truth.

  events   Mermaid, because twelve nodes is what Mermaid is for.

  map      SVG, because hundreds of places is what Mermaid is not for. A graph that size is
           unreadable and slow to lay out, and no styling fixes it. SVG over the existing
           0-100 grid needs no projection maths and stays diffable.

**Five eras draw a world; the sixth draws three points.** The coast, the regions and the
Saraswati are traced off `dump/Partial_map.png`, which is the only picture canon has of its own
geography. After the Great Shattering canon knows three field-map coordinates and no ground at
all, and those coordinates are cataclysm-shaped by `field_map.schema.json`'s own account -- so
drawing them over the earlier coast put two of the three field maps in open sea.

That is not a gap in the atlas. The difference between the five maps and the sixth is the only
picture of the Shattering canon is going to have, since the event itself stays unwritten on
purpose. Ruling in DESIGN.md.

    python utils/generate_atlas.py                          # every era
    python utils/generate_atlas.py --era epoch_post_cataclysm
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from book_nav import nav
from canon_epochs import in_era, load_epochs, state_in_era
from canon_events import load_events, ordered

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database"
OUT_MD = BASE / "docs" / "atlas.md"
OUT_MAPS = BASE / "docs" / "atlas"

# Folders worth counting in a census. Schemas validate canon rather than being it, and the
# epoch table is the thing being indexed by, not a thing to index.
SKIP = {"schemas", "timeline"}

# What a reader wants named first.
ORDER = [
    "regions", "places", "settlements", "field_maps", "points_of_interest",
    "characters", "npcs", "factions", "events", "artifacts", "mythology",
    "discoveries", "field_questions", "vocabulary", "fauna", "flora",
]


def load_all() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in sorted(DB.iterdir()):
        if not d.is_dir() or d.name in SKIP:
            continue
        entities = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("*.json"))]
        if entities:
            out[d.name] = entities
    return out


def label(text: str) -> str:
    """Mermaid node text. Quotes end a label and brackets end a node."""
    return text.replace('"', "'").replace("[", "(").replace("]", ")")


def xml_text(text: str) -> str:
    """Text safe inside an SVG element.

    SVG is XML, which predefines five entities and no more -- `&middot;` and friends are a
    parse error, not a dot. And canon really does contain an ampersand: `region_shattered_sea`
    is named "Shattered Sea & Mappa Mundi", which would have produced an unparseable map the
    day a region was ever plotted.
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def census(folders: dict[str, list[dict]], epoch_id: str) -> list[tuple[str, int, int]]:
    """(folder, dated to this era, timeless) — only folders with something present."""
    rows = []
    for name in [f for f in ORDER if f in folders] + [f for f in folders if f not in ORDER]:
        dated = timeless = 0
        for e in folders[name]:
            claims = any(k for k in e if "epoch" in k and k != "epoch_founded" and e[k])
            if not claims:
                timeless += 1
            elif in_era(e, epoch_id):
                dated += 1
        if dated or timeless:
            rows.append((name, dated, timeless))
    return rows


def event_graph(events: list[dict], epoch_id: str) -> str | None:
    here = [e for e in events if e.get("epoch") == epoch_id]
    if not here:
        return None
    node = {e["id"]: f"E{i}" for i, e in enumerate(here)}
    lines = ["```mermaid", "graph TD"]
    for e in here:
        title = e.get("title") or e["id"]
        if e.get("sample"):
            title += " (sample)"
        lines.append(f'    {node[e["id"]]}["{label(title)}"]')
    for e in here:
        for succ in e.get("successors") or []:
            if succ in node:
                lines.append(f'    {node[e["id"]]} --> {node[succ]}')
    lines.append("```")
    return "\n".join(lines)


# What a region's ground looks like. Presentation, so it lives here rather than in canon:
# `database/biomes.json` says which biomes exist and which the game can draw, and deliberately
# has no opinion on colour. The region's first biome wins -- a region is one wash, not a survey.
TERRAIN = {
    "desert":     ("#D9C89A", "#3B3524"),
    "plains":     ("#A8BE84", "#2A3520"),
    "forest":     ("#7EA46E", "#20301E"),
    "wetland":    ("#8FAD9E", "#1E2E2A"),
    "hills":      ("#B3B183", "#302E20"),
    "mountains":  ("#A9A79C", "#2C2B26"),
    "river":      ("#8FB3C4", "#1D2E36"),
    "coast":      ("#D8CBA0", "#393322"),
    "sea":        ("#7FA6C0", "#1B2C36"),
    "lava_field": ("#C4735A", "#3A1C15"),
}
LAND = ("#C8CBA8", "#2A3026")
SEA = ("#93B4CB", "#18242E")


def ring(points: list[list[float]]) -> str:
    return " ".join(f"{x},{y}" for x, y in points)


# The traced coastline is the world *before* the Great Shattering, and after it canon knows
# three points and no ground at all. Drawing both together puts two of the three field maps in
# open sea -- their coordinates are cataclysm-shaped by `field_map.schema.json`'s own account,
# and the map they would sit on no longer exists.
#
# So the last era gets the three points on bare grid, and the five before it get the world. That
# is not a gap in the atlas; it is the Shattering, drawn.
UNSHAPED = {"epoch_post_cataclysm"}

# An era whose arrangement canon does not claim to know, which is a stronger statement than
# UNSHAPED and gets no map at all rather than a map without a coastline.
#
# The Prehistoric era is too old for the world `Partial_map.png` draws. That picture shows a
# living Harappa and a standing university -- it is the Civilization Dawn world, and the grid
# traced off it describes that arrangement. Putting the Vanaras on it would say canon knows
# where the Age of Vanaras sat, and canon does not: it predates every landmark the map is
# built from. The census still lists everything the era holds; only the picture is withheld.
#
# UNSHAPED is the weaker case. The Post-Cataclysm still draws its points, because the three
# field-map anchors *are* cataclysm-shaped and correct for it -- what it has lost is the
# coastline, not the arrangement.
UNMAPPED = {"epoch_prehistoric"}


def shapes(folders: dict[str, list[dict]], epoch_id: str) -> tuple[list[dict], list[dict]]:
    """Landmasses and regions with a traced outline that exist in this era."""
    if epoch_id in UNSHAPED:
        return [], []
    land = [e for e in folders.get("places", []) if e.get("extent") and in_era(e, epoch_id)]
    ground = [e for e in folders.get("regions", []) if e.get("extent") and in_era(e, epoch_id)]
    return land, ground


def courses(folders: dict[str, list[dict]], epoch_id: str) -> list[dict]:
    """Rivers and routes -- anything canon gives a line rather than a ring.

    Held back on the same era as the coastline: a river without its valley is a stripe in the
    sea.
    """
    if epoch_id in UNSHAPED:
        return []
    return [e for e in folders.get("places", []) if e.get("path") and in_era(e, epoch_id)]


def placed(folders: dict[str, list[dict]], epoch_id: str) -> list[dict]:
    """Everything with coordinates that exists in this era, resolved to its state then."""
    out = []
    for name in ("field_maps", "places", "settlements"):
        for entity in folders.get(name, []):
            if not in_era(entity, epoch_id):
                continue
            resolved = state_in_era(entity, epoch_id)
            coords = resolved.get("coordinates")
            if isinstance(coords, dict) and "x" in coords and "y" in coords:
                out.append({**resolved, "_folder": name})
    return out


def svg_map(points: list[dict], epoch_name: str,
            land: list[dict] | None = None, ground: list[dict] | None = None,
            lines: list[dict] | None = None) -> str:
    """The 0-100 grid, drawn directly. y grows downward, which is the ruling and also SVG.

    Sea, then the landmasses, then each region washed by its first biome, then whatever canon
    has actually placed -- in that order, because that is the order the world is in.
    """
    land = land or []
    ground = ground or []
    W = H = 100
    pad = 14
    light = "".join(f".t-{b}{{fill:{c[0]}}}" for b, c in TERRAIN.items())
    dark = "".join(f".t-{b}{{fill:{c[1]}}}" for b, c in TERRAIN.items())
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W + pad * 2} {H + pad * 2}" '
        f'width="720" role="img" aria-label="Map of {xml_text(epoch_name)}">',
        "<style>",
        "  .bg{fill:#E7EAE6}.grid{stroke:#CBD1CB;stroke-width:.3}.edge{stroke:#AFB8B1;stroke-width:.6}",
        "  .dot{fill:#2C5C8F}.dot-place{fill:#7E6A2E}",
        "  .lbl{fill:#17201F;font:3.2px Archivo,sans-serif}",
        "  .cap{fill:#7D8A86;font:2.6px 'JetBrains Mono',monospace}",
        f"  .sea{{fill:{SEA[0]}}} .land{{fill:{LAND[0]}}}",
        "  polygon{stroke:#7E8A76;stroke-width:.25}",
        "  .rgn{fill:#39402F;font:2.7px Archivo,sans-serif;font-style:italic;opacity:.9}",
        "  .course{fill:none;stroke:#5B87A8;stroke-width:.8;stroke-linejoin:round;stroke-linecap:round}",
        "  .course-lbl{fill:#2F5470;font:2.2px Archivo,sans-serif;font-style:italic}",
        f"  {light}",
        "  @media(prefers-color-scheme:dark){",
        "   .bg{fill:#121817}.grid{stroke:#28322F}.edge{stroke:#3E4C4E}",
        "   .dot{fill:#74A8DA}.dot-place{fill:#CBAE6A}.lbl{fill:#E2E7E3}.cap{fill:#78857F}",
        f"   .sea{{fill:{SEA[1]}}} .land{{fill:{LAND[1]}}}",
        "   polygon{stroke:#3A4436} .rgn{fill:#9FB09A}",
        "   .course{stroke:#6E9CBD} .course-lbl{fill:#9DBDD4}",
        f"   {dark}",
        "  }",
        "</style>",
        f'<rect class="bg" x="{-pad}" y="{-pad}" width="{W + pad * 2}" height="{H + pad * 2}"/>',
    ]

    # Sea only where the world is; beyond the grid stays paper.
    if land or ground:
        parts.append(f'<rect class="sea" x="0" y="0" width="{W}" height="{H}"/>')
    for e in land:
        parts.append(f'<polygon class="land" points="{ring(e["extent"])}"/>')
    for e in ground:
        biome = (e.get("biomes") or ["plains"])[0]
        cls = f"t-{biome}" if biome in TERRAIN else "t-plains"
        parts.append(f'<polygon class="{cls}" points="{ring(e["extent"])}"/>')
        xs = [p[0] for p in e["extent"]]
        ys = [p[1] for p in e["extent"]]
        parts.append(
            f'<text class="rgn" x="{sum(xs) / len(xs):.1f}" y="{sum(ys) / len(ys):.1f}" '
            f'text-anchor="middle">{xml_text(e["name"])}</text>'
        )

    # Rivers over the ground they cut through, under everything standing on it.
    for e in lines or []:
        parts.append(f'<polyline class="course" points="{ring(e["path"])}"/>')
        hx, hy = e["path"][len(e["path"]) // 2]
        parts.append(
            f'<text class="course-lbl" x="{hx:.1f}" y="{hy - 1.4:.1f}" '
            f'text-anchor="middle">{xml_text(e["name"])}</text>'
        )

    for g in range(0, 101, 20):
        parts.append(f'<line class="grid" x1="{g}" y1="0" x2="{g}" y2="{H}"/>')
        parts.append(f'<line class="grid" x1="0" y1="{g}" x2="{W}" y2="{g}"/>')

    by_id = {p["id"]: p for p in points}
    for p in points:
        for other in p.get("neighbours") or []:
            q = by_id.get(other)
            if q and p["id"] < other:
                parts.append(
                    f'<line class="edge" x1="{p["coordinates"]["x"]}" y1="{p["coordinates"]["y"]}"'
                    f' x2="{q["coordinates"]["x"]}" y2="{q["coordinates"]["y"]}"/>'
                )

    xs = [p["coordinates"]["x"] for p in points]
    for p in points:
        x, y = p["coordinates"]["x"], p["coordinates"]["y"]
        cls = "dot" if p["_folder"] == "field_maps" else "dot-place"
        anchor = "end" if x == max(xs) else ("start" if x == min(xs) else "middle")
        dx = -2 if anchor == "end" else (2 if anchor == "start" else 0)
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="1.5"/>')
        parts.append(
            f'<text class="lbl" x="{x + dx}" y="{y - 3}" text-anchor="{anchor}">'
            f'{xml_text(p.get("name") or p["id"])}</text>'
        )
    # A literal middle dot, not `&middot;` -- that entity is undefined in XML.
    parts.append(f'<text class="cap" x="0" y="{H + 8}">north is up · 0-100 grid</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--era", help="one epoch id; default is all of them")
    args = ap.parse_args()

    epochs = load_epochs()
    if args.era:
        epochs = [e for e in epochs if e["id"] == args.era]
        if not epochs:
            print(f"No such epoch: {args.era}")
            return 1

    folders = load_all()
    events = ordered(load_events())
    OUT_MAPS.mkdir(parents=True, exist_ok=True)

    doc = [
        "# The Atlas of South of Tethys",
        "",
        nav("atlas.md"),
        "",
        "_Generated from `database/` by `utils/generate_atlas.py`. Do not edit by hand._",
        "",
        "Each era below is canon as it stood then. An entity that names no epoch is present in "
        "every era — silence means timeless, not unplaced, which is the ruling in `DESIGN.md` "
        "and what fauna has always meant.",
        "",
    ]

    mapped = 0
    for ep in epochs:
        eid, name = ep["id"], ep.get("name") or ep["id"]
        doc += [f"## {name}", "", f"**{ep.get('range', 'undated')}**", ""]
        if ep.get("notes"):
            doc += [f"> {ep['notes']}", ""]

        rows = census(folders, eid)
        doc += ["| | dated to this era | timeless |", "|---|---:|---:|"]
        for folder, dated, timeless in rows:
            doc.append(f"| {folder.replace('_', ' ')} | {dated or ''} | {timeless or ''} |")
        doc.append("")

        graph = event_graph(events, eid)
        if graph:
            doc += ["### Events", "", graph, ""]

        points = placed(folders, eid) if eid not in UNMAPPED else []
        land, ground = shapes(folders, eid)
        lines = courses(folders, eid)
        # Ground is enough for a map. An era can have coastline and regions without a single
        # placed settlement, and that is still a picture of somewhere.
        if eid in UNMAPPED:
            doc += [
                "### Map",
                "",
                "*No map is drawn for this era.* The grid canon uses is traced off "
                "`dump/Partial_map.png`, which shows a living Harappa and a standing "
                "university -- it is a picture of the Civilization Dawn world. This era "
                "predates every landmark that map is built from, so placing anything on it "
                "would claim a geography canon does not have. What the era holds is in the "
                "census above.",
                "",
            ]
        elif points or ground:
            mapped += 1
            svg_path = OUT_MAPS / f"{eid}.svg"
            svg_path.write_text(svg_map(points, name, land, ground, lines) + "\n", encoding="utf-8")
            rel = f"atlas/{eid}.svg"
            doc += [
                "### Map",
                "",
                f"![Map of {name}]({rel})",
                "",
                f"{len(ground)} region(s) traced, {len(points)} place(s) plotted. "
                f"[Open the SVG]({rel})",
                "",
            ]
        else:
            doc += [
                "### Map",
                "",
                "_No map for this era, deliberately._ The only coordinates canon holds belong to "
                "the three field maps, and their layout describes the world *after* the Great "
                "Shattering. Earlier eras are not drawn because **the Shattering is withheld on "
                "purpose** — canon keeps its consequences and not its account, since working it "
                "out is what the player is there to do, and the shape of the world before it is "
                "part of what is being withheld. Absent by design rather than pending. The "
                "timeline, events and census above are everything canon states about this era. "
                "See `DESIGN.md`.",
                "",
            ]

    OUT_MD.write_text("\n".join(doc), encoding="utf-8")
    print(f"✅ Atlas → {OUT_MD.relative_to(BASE)}")
    print(f"   {len(epochs)} era(s), {mapped} with a map, {sum(len(v) for v in folders.values())} entities read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
