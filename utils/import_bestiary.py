"""Import the Jambhudweepa bestiary into database/ as canonical entities.

Phase 1.2 of the canon/game integration. 4000BCESaraswathy authors ~300 species as
prose in docs/bestiary.md and derives data/creatures.json + data/flora.json from it
with tools/build-species-data.js. That made the game repo a second entity store for
the same fiction, which is what CONTEXT.md forbids -- and it has already produced
seven binomial contradictions between the two repos.

This script moves the bestiary into database/ so there is one source of truth. The
parse and the biome/mood/rarity heuristics are a faithful port of
tools/build-species-data.js, so the first export back out to the game is a no-op.
The heuristics are only a starting point: once here, biomes and rarity are authored
canon fields to be corrected by hand rather than re-guessed from prose.

Three populations, three treatments:

  in both repos   merge -- add the bestiary's fields, never overwrite canon's.
                  This is what implements "canon wins" on the seven disputed
                  binomials: an existing `scientific` value is simply never touched.
  bestiary only   create a new entity.
  canon only      leave the authored content alone, but mark it `placement: lore`
                  if it has no biomes, so it stays out of the encounter table until
                  someone tags it by hand.

Also rescues the content that lives only inside tools/build-species-data.js and
would be deleted outright when that script is retired: five prototype starter
creatures, and the fillGaps biome assignments that keep plains/settlement/landmark
from being empty.

Placement rules, as settled (see database/README.md for the full statement):

  Asura-tainted   placed like anything else, at mythic rarity. They are met
                  occasionally and are meant to unsettle. The game weights picks
                  by rarity, which is what keeps "occasionally" true -- without
                  that weighting, uniform picking put a horror in every second
                  village.
  Sky species     never placed. The floating islands are a planned mode and these
                  are its content, held in reserve. They carry a placement_note
                  saying so, because an empty `biomes` list otherwise reads as an
                  untagged entity and invites someone to spend them on ground.
  sentient        taxonomy only, not a placement rule. In-world the Harappans
                  regard these lineages as animals, so a sentient species in the
                  encounter table is correct.
  everything else biomes from prose keywords, preferring agreement with the
                  species' own region; anything that matches nothing lands as
                  lore and needs tagging by hand.

Dry run by default. Pass --apply to write.

    python utils/import_bestiary.py
    python utils/import_bestiary.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_GAME_REPO = REPO.parent / "4000BCESaraswathy"

# --- ported from tools/build-species-data.js -------------------------------------

REGIONS = {
    "1": "saraswati-godavari-deltas",
    "2": "narmada-vindhya",
    "3": "gedrosian-taklamakan",
    "4": "shattered-sea-mappa-mundi",
    "5": "ganges-lava-sea",
    "6": "tethys-sky-routes",
    "7": "asura-conjurations",
}

# Where a region's species land when nothing more specific is detected in the prose.
# This table used to live in tools/build-species-data.js. It is canon now: each region
# entity carries `bestiary_region` and `biomes`, and this is read from them. The literal
# below is only the bootstrap fallback for a checkout whose regions predate Phase 1.3.
_REGION_BIOMES_FALLBACK = {
    "saraswati-godavari-deltas": ["wetland", "river"],
    "narmada-vindhya": ["hills", "mountains"],
    "gedrosian-taklamakan": ["desert"],
    "shattered-sea-mappa-mundi": ["sea", "forest"],
    "ganges-lava-sea": ["mountains"],
    "tethys-sky-routes": [],
    "asura-conjurations": [],
}


def load_region_biomes() -> dict[str, list[str]]:
    mapping = {}
    for f in sorted((REPO / "database" / "regions").glob("*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        if "bestiary_region" in payload:
            mapping[payload["bestiary_region"]] = payload.get("biomes", [])
    if not mapping:
        return dict(_REGION_BIOMES_FALLBACK)
    # Asura conjurations are a taxonomy tag, not a place, so they have no region entity.
    mapping.setdefault("asura-conjurations", [])
    return mapping


REGION_BIOMES = load_region_biomes()

# Read biome first from the prose, which is more reliable than the region heading:
# Section 1 alone carries eight species that describe other regions entirely.
BIOME_HINTS = [
    ("sea", r"\b(sea|ocean|marine|oceanic|reef|coral|lagoon|pelagic|open water|whale|abyssal|deep[- ]sea)\b"),
    ("coast", r"\b(coast|coastal|shore|shoreline|beach|estuar\w*|brackish|mangrove|tidal|tide|shorebird|sandy riverbank|salt marsh)\b"),
    ("river", r"\b(river\w*|stream\w*|tributar\w*|riverbed|freshwater|stepwell|riverside)\b"),
    ("wetland", r"\b(marsh\w*|swamp\w*|wetland|reed\w*|bog|delta pool|lotus|mud[- ]?pool|shallow pool)\b"),
    ("forest", r"\b(forest|canopy|canopies|jungle|arboreal|woodland|foliage|leaf litter|tree\w*|thicket|grove|vine)\b"),
    ("hills", r"\b(hill\w*|cliff\w*|ledge\w*|scree|plateau|crag\w*|ridge\w*|foothill\w*)\b"),
    ("mountains", r"\b(mountain\w*|peak\w*|summit|alpine|highland\w*|glacier|glacial|volcanic|basalt|caldera|lava|magma|cave\w*)\b"),
    ("desert", r"\b(desert|dune\w*|sand\w*|arid|salt flat\w*|salt plain\w*|oasis|wastes)\b"),
    ("settlement", r"\b(settlement|village|town|city|street\w*|court\w*|temple\w*|Harappa\w*|fortress|ruins?)\b"),
    ("plains", r"\b(plain\w*|grassland|steppe|meadow|savanna|open grass)\b"),
]

MOOD_HINTS = [
    ("uncanny", r"\b(asura|mutated|cursed|spectral|construct|corrupt\w*|resurrect\w*|unnatural|wraith|shadow|mantras?)\b"),
    ("luminous", r"\b(glow\w*|glowing|bioluminescen\w*|shimmer\w*|iridescen\w*|phosphor\w*|luminous)\b"),
    ("fearsome", r"\b(venom\w*|toxic|predator\w*|ambush\w*|aggressive|hunts?|hunting|prowl\w*|razor|paralyz\w*|deadly)\b"),
    ("graceful", r"\b(glide\w*|gliding|soar\w*|drift\w*|dances?|dancing|weightless|float\w*)\b"),
    ("playful", r"\b(playful|young|calf|agile|leap\w*|sprint\w*|nimble)\b"),
    ("patient", r"\b(patient\w*|slow\w*|waits?|waiting|burrow\w*|buried|long-lived|camouflag\w*)\b"),
    ("clever", r"\b(intelligent|problem-solving|cognitavi|symbiotic|complex|navigator|wisdom)\b"),
]

# Sky species have no equivalent among the ten ground biomes, and their prose mentions
# terrain they only fly over ("aero-mangrove", "sky coral"), which would mis-file them.
# The marker also catches strays: the Sky-Faring Grasshopper is filed under Section 1 but
# migrates between floating islands.
# "airborne" was in this list and was too loose: the Toxic Red Spore-Moss "releases airborne
# spores" and was pulled into the sky reserve, a plateau moss labelled as content for a mode
# it has nothing to do with. Every genuine sky species is caught by its region; the marker
# only has to catch strays filed under the wrong section.
SKY_MARKER = r"\b(floating island\w*|sky[- ]\w+|aero[- ]\w+|prana|low[- ]gravity|lodestone|cloud[- ]weaver)\b"

# Sky species are a reserve, not a backlog. The floating islands are a planned mode and
# these are its content, waiting -- so each says so on itself, or the next pass over empty
# `biomes` reads them as untagged and spends them on ground biomes.
# Naraka natives. Their water is not the Saraswati's, so they must not be placed in ordinary
# river and wetland tiles by the biome keywords in their own prose -- "swims in the sulfuric
# rivers of Naraka" would otherwise land a rift snake in the delta. All six matches in the
# bestiary are locative ("of the Naraka rivers", "grows near underworld rifts", "rituals in
# Naraka"), so the plain word is a precise enough marker; "rift" and "portal" are not, and
# catch lava rifts and the Sylvian Gate.
NARAKA_MARKER = r"\b(naraka|underworld)\b"

NARAKA_NOTE = (
    "Native to the Naraka rifts, not to delta water. It enters this realm through the Dwarka Gate "
    "(settlement_dwarka; see event_shadow_pact and event_naraka_portal), so it should be met near a "
    "gate and nowhere else. `underworld` is not renderable yet, so the export holds it as lore; when "
    "the Dwarka Gate exists as a landmark, add that biome."
)

# The established crossing between Naraka and this realm.
NARAKA_CROSSING = ["settlement_dwarka"]

SKY_RESERVE_NOTE = (
    "Lives on the floating islands. `sky_island` and its neighbours are real canon biomes but are "
    "not renderable yet, so the export holds this as lore until a sky mode exists. This is a stated "
    "home, not an untagged entity."
)

ENTRY_RE = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*\s+—\s+(.+)$")
NAMED_RE = re.compile(r"^(.*?)\s*\(\*(.+?)\*\)\s*$")


def slug(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _hits(patterns, text):
    return [name for name, pat in patterns if re.search(pat, text, re.IGNORECASE)]


def place_for(text: str, region: str) -> tuple[list[str], str]:
    detected = list(dict.fromkeys(_hits(BIOME_HINTS, text)))[:3]

    if region == "tethys-sky-routes" or re.search(SKY_MARKER, text, re.IGNORECASE):
        # A real home, not a blank. `sky_island` and its neighbours are canon biomes that the
        # game cannot render, so the export turns them into `lore` on its own -- which means
        # the species can say where it lives without an empty list having to mean two things.
        sky = ["sky_island"]
        if re.search(r"underside|attach|cling|adhesive|beneath the island|calcified|roots? plunge|shelter", text, re.I):
            sky.append("sky_underside")
        if re.search(r"glid|soar|migrat|drift|balloon|skim|fly|flying|between islands|rudder|hollow bones", text, re.I):
            sky.append("open_sky")
        return sky, "lore"

    # Checked before the biome keywords, which would otherwise read "sulfuric rivers of Naraka"
    # as a river and put a rift snake in the Saraswati.
    if re.search(NARAKA_MARKER, text, re.IGNORECASE):
        return ["underworld"], "lore"

    # Prose keywords bleed across regions: a volcanic moth mentions "ash-banyan trees"
    # and lands in forest. When the prose agrees with the species' own region, keep only
    # that agreement. Species whose prose matches nothing in their region keep the prose
    # -- that is what re-files the Section 1 strays.
    home = [b for b in REGION_BIOMES.get(region, []) if b in detected]
    if home:
        return home, "encounter"

    # Asura conjurations are placed like anything else. They used to be forced to "lore"
    # here pending the cozy-tone question in docs/bestiary.md; that is settled -- they are
    # met occasionally and are meant to unsettle. `rarity_for` gives them mythic, and the
    # game weights picks by rarity, which is what keeps "occasionally" true. Their region
    # contributes no fallback biomes, so one whose prose matches nothing still lands as
    # lore and needs tagging by hand.
    biomes = detected or list(REGION_BIOMES.get(region, []))
    return biomes, ("encounter" if biomes else "lore")


def mood_for(text: str) -> str:
    hits = _hits(MOOD_HINTS, text)
    return hits[0] if hits else "watchful"


def rarity_for(text: str, region: str) -> str:
    if region == "asura-conjurations" or re.search(r"\b(mythic|legendary|colossal|titan)\b", text, re.IGNORECASE):
        return "mythic"
    if region in ("ganges-lava-sea", "tethys-sky-routes"):
        return "rare"
    if re.search(r"\b(giant|massive|elite|rare|hyper-intelligent)\b", text, re.IGNORECASE):
        return "rare"
    return "common"


# The six prototype creatures predate the bestiary and live only in the JS. Retiring
# that script without these would delete five of them outright -- cloud-antelope is one
# of only three creatures covering the `landmark` biome. river-otter already reached
# canon as fauna_river_otter, so it merges rather than being created.
STARTERS = [
    ("River Otter", "playful", ["river", "wetland", "forest"],
     "A slick shape rolls through the shallows, leaving rings of silver water behind."),
    ("Painted Deer", "gentle", ["plains", "forest"],
     "A small deer watches from the grass, its coat patterned like fallen petals."),
    ("Monsoon Crane", "graceful", ["wetland", "river", "coast"],
     "Tall white birds step between reeds as if reading the rain."),
    ("Hill Macaque", "curious", ["hills", "forest", "settlement"],
     "A macaque studies your satchel, then pretends it was only admiring the view."),
    ("Shell Turtle", "patient", ["coast", "river"],
     "A turtle rests where river sand meets the tide, carrying a map of scratches on its shell."),
    ("Cloud Antelope", "mythic", ["mountains", "hills"],
     "For a breath, an antelope-shaped cloud stands on a ridge before dissolving into mist."),
]

# Editorial decisions encoded only in the JS: which species covers a biome the bestiary
# left empty. Lose these and plains, settlement and landmark go silent in play.
FLORA_BIOME_FALLBACK = {
    "plains": ["tawny-sagebrush", "golden-sun-barley"],
    "settlement": ["sweet-indigo", "oasis-date-palm"],
    "landmark": ["mappa-mundi-banyan", "silver-leaved-oracle-fig"],
}
CREATURE_BIOME_FALLBACK = {
    "landmark": ["cloud-antelope", "indus-unicorn", "vanga-pearl-guide"],
}

# Sovereign avian-dinosaurid cultures, not wildlife: bird-fortresses, cloud monasteries
# and a maritime alliance with the Vanga league (AI_CONTEXT.md:998-1006). Flagged so the
# migration does not quietly cement them into the random encounter table.
SENTIENT_GENERA = {"cognitavi", "silvanus", "sylvianus"}
SENTIENT_NAMES = {"nagaraptor", "vajraptor", "kuktush"}


def is_sentient(name: str, binomial: str | None) -> bool:
    genus = (binomial or "").split(" ")[0].lower()
    return genus in SENTIENT_GENERA or slug(name).replace("-", " ") in SENTIENT_NAMES


# --- bestiary parsing -------------------------------------------------------------


def parse_bestiary(path: Path, kind: str) -> list[dict]:
    entries: list[dict] = []
    region = None
    listing = None

    for line in path.read_text(encoding="utf-8").splitlines():
        section = re.match(r"^## Section (\d+):", line)
        if section:
            region, listing = REGIONS[section.group(1)], None
            continue
        if re.match(r"^### Fauna", line):
            listing = "fauna"
            continue
        if re.match(r"^### Flora", line):
            listing = "flora"
            continue
        if line.startswith("## "):
            region, listing = None, None
            continue
        if listing != kind or not region:
            continue

        entry = ENTRY_RE.match(line)
        if not entry:
            continue

        heading, description = entry.group(1), entry.group(2)
        binomial = None
        named = NAMED_RE.match(heading)
        if named:
            heading, binomial = named.group(1).strip(), named.group(2).strip()

        text = f"{heading} {description}"
        biomes, placement = place_for(text, region)
        record = {
            "name": heading,
            "binomial": binomial,
            "region": region,
            "sky": region == "tethys-sky-routes" or bool(re.search(SKY_MARKER, text, re.IGNORECASE)),
            "naraka": bool(re.search(NARAKA_MARKER, text, re.IGNORECASE)),
            "biomes": biomes,
            # Creatures are met; plants are simply there.
            "placement": "flavour" if placement == "encounter" and kind == "flora" else placement,
            "rarity": rarity_for(text, region),
            "journal_prompt": description.strip(),
        }
        if kind == "fauna":
            record["mood"] = mood_for(text)
        entries.append(record)
    return entries


# --- canon side -------------------------------------------------------------------


def load_canon(kind: str) -> dict[str, list[tuple[Path, dict]]]:
    """Existing entities grouped by normalised name.

    A list rather than a single entry because names are not unique: the bestiary
    carries two Lava-Vent Tubeworms, separated only by binomial (Riftia vulcanica and
    Riftia asurica). Keying by name alone let one silently shadow the other, so a
    re-run merged the second record's fields into the first entity.
    """
    out: dict[str, list[tuple[Path, dict]]] = {}
    folder = REPO / "database" / kind
    for f in sorted(folder.glob("*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        out.setdefault(payload["name"].strip().lower(), []).append((f, payload))
    return out


def match_canon(candidates: list[tuple[Path, dict]], rec: dict, consumed: set[str]) -> tuple[Path, dict] | None:
    """Pick the entity a bestiary record refers to, preferring an agreeing binomial."""
    free = [c for c in candidates if c[1]["id"] not in consumed]
    if not free:
        return None
    if rec.get("binomial"):
        for path, payload in free:
            if payload.get("scientific") == rec["binomial"]:
                return path, payload
    return free[0]


def entity_id(kind: str, name: str, taken: set[str], binomial: str | None) -> str:
    base = f"{kind}_{slug(name).replace('-', '_')}"
    if base not in taken:
        return base
    # The bestiary carries one genuine collision (Riftia Lava-Vent Tubeworm appears twice
    # as vulcanica and asurica). Disambiguate by epithet rather than a bare -2 suffix.
    epithet = (binomial or "").split(" ")[-1].lower()
    if epithet:
        candidate = f"{base}_{slug(epithet).replace('-', '_')}"
        if candidate not in taken:
            return candidate
    n = 2
    while f"{base}_{n}" in taken:
        n += 1
    return f"{base}_{n}"


def build_new(kind: str, rec: dict, ident: str) -> dict:
    payload = {
        "id": ident,
        "type": kind,
        "name": rec["name"],
        "scientific": rec["binomial"],
        "region": rec["region"],
        "biomes": rec["biomes"],
        "placement": rec["placement"],
        "rarity": rec["rarity"],
        "journal_prompt": rec["journal_prompt"],
        "source_index": rec["source_index"],
        "canon": "primary",
        "sources": ["docs/bestiary.md"],
    }
    # Only the sky and rift sets are deliberate holds. A ground species whose prose matched no
    # biome keyword is genuinely untagged and must not be labelled as one.
    if rec.get("naraka"):
        payload["crosses_at"] = list(NARAKA_CROSSING)
        payload["placement_note"] = NARAKA_NOTE
    elif rec.get("sky"):
        payload["placement_note"] = SKY_RESERVE_NOTE
    if kind == "fauna":
        payload["mood"] = rec["mood"]
        if is_sentient(rec["name"], rec["binomial"]):
            payload["sentient"] = True
    return payload


# Fields the bestiary can contribute. Anything already present in canon is left alone --
# this is what implements canon-wins on the seven disputed binomials.
MERGEABLE = ("region", "biomes", "placement", "rarity", "journal_prompt", "mood", "source_index",
             "crosses_at")


def merge_into(existing: dict, rec: dict, kind: str) -> tuple[dict, list[str]]:
    added, kept = [], []
    for field in MERGEABLE:
        if field not in rec:
            continue
        if field not in existing:
            existing[field] = rec[field]
            added.append(field)
    if rec.get("binomial") and existing.get("scientific") not in (None, "", rec["binomial"]):
        kept.append(f"scientific: kept {existing['scientific']!r}, bestiary said {rec['binomial']!r}")
    elif rec.get("binomial") and not existing.get("scientific"):
        existing["scientific"] = rec["binomial"]
        added.append("scientific")
    if kind == "fauna" and is_sentient(rec["name"], existing.get("scientific")) and "sentient" not in existing:
        existing["sentient"] = True
        added.append("sentient")
    sources = existing.setdefault("sources", [])
    if "docs/bestiary.md" not in sources:
        sources.append("docs/bestiary.md")
    return existing, kept


def coverage(entities: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for e in entities:
        if e.get("placement") == "lore":
            continue
        for b in e.get("biomes") or []:
            out[b] = out.get(b, 0) + 1
    return out


def fill_gaps(label: str, entities: list[dict], fallbacks: dict, walkable: list[str], log: list[str]) -> None:
    by_slug = {slug(e["name"]): e for e in entities}
    for biome in walkable:
        if coverage(entities).get(biome):
            continue
        filled = [by_slug[s] for s in fallbacks.get(biome, []) if s in by_slug]
        if not filled:
            log.append(f"  ! no {label} for biome {biome!r} and no fallback available")
            continue
        for e in filled:
            e.setdefault("biomes", [])
            if biome not in e["biomes"]:
                e["biomes"].append(biome)
        log.append(f"  filled empty {label} biome {biome!r} with " + ", ".join(e["name"] for e in filled))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-repo", type=Path, default=DEFAULT_GAME_REPO,
                    help="path to 4000BCESaraswathy (default: sibling of this repo)")
    ap.add_argument("--apply", action="store_true", help="write files; otherwise dry run")
    args = ap.parse_args()

    bestiary = args.game_repo / "docs" / "bestiary.md"
    biomes_file = args.game_repo / "data" / "biomes.json"
    if not bestiary.exists():
        print(f"ERROR: bestiary not found at {bestiary}", file=sys.stderr)
        return 1

    walkable = [b["id"] for b in json.loads(biomes_file.read_text(encoding="utf-8")) if b.get("walkable")]

    created, merged, retained, log = [], [], [], []
    all_entities: dict[str, list[dict]] = {"fauna": [], "flora": []}

    for kind in ("fauna", "flora"):
        canon = load_canon(kind)
        taken = {p["id"] for entries in canon.values() for _, p in entries}
        records = parse_bestiary(bestiary, kind)
        if kind == "fauna":
            # The game assembles [...STARTERS, ...parseBestiary('fauna')], and array order
            # decides which species pickFor lands on for a given tile -- it is part of the
            # seed contract, not presentation. Record it so the export can reproduce it
            # without re-reading the bestiary.
            records = [
                {"name": n, "binomial": None, "region": "prototype-starters", "biomes": list(b),
                 "placement": "encounter", "rarity": "common", "mood": m, "journal_prompt": j}
                for n, m, b, j in STARTERS
            ] + records
        for i, rec in enumerate(records):
            rec["source_index"] = i

        touched: dict[str, dict] = {}
        consumed: set[str] = set()
        for rec in records:
            key = rec["name"].strip().lower()
            hit = match_canon(canon[key], rec, consumed) if key in canon else None
            if hit:
                path, payload = hit
                consumed.add(payload["id"])
                payload, kept = merge_into(payload, rec, kind)
                retained.extend(f"{payload['id']}: {k}" for k in kept)
                touched[str(path)] = payload
                merged.append(payload["id"])
                all_entities[kind].append(payload)
            else:
                ident = entity_id(kind, rec["name"], taken, rec["binomial"])
                taken.add(ident)
                payload = build_new(kind, rec, ident)
                touched[str(REPO / "database" / kind / f"{ident}.json")] = payload
                created.append(ident)
                all_entities[kind].append(payload)

        # Canon-only entities: authored here, absent from the bestiary. Leave the prose
        # alone but keep them out of the encounter table until tagged by hand.
        for entries in canon.values():
            for path, payload in entries:
                if payload["id"] in consumed:
                    continue
                if not payload.get("biomes"):
                    payload.setdefault("biomes", [])
                    payload.setdefault("placement", "lore")
                    touched[str(path)] = payload
                all_entities[kind].append(payload)

        fallbacks = CREATURE_BIOME_FALLBACK if kind == "fauna" else FLORA_BIOME_FALLBACK
        fill_gaps(kind, all_entities[kind], fallbacks, walkable, log)

        if args.apply:
            for path_str, payload in touched.items():
                Path(path_str).write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )

    sentient = [e["id"] for e in all_entities["fauna"] if e.get("sentient")]
    untagged = [e["id"] for k in all_entities for e in all_entities[k] if not e.get("biomes")]

    print(f"{'APPLIED' if args.apply else 'DRY RUN — nothing written'}")
    print(f"  created {len(created)}   merged {len(merged)}")
    print(f"  fauna total {len(all_entities['fauna'])}   flora total {len(all_entities['flora'])}")
    for line in log:
        print(line)
    print(f"\n  canon binomials retained over the bestiary: {len(retained)}")
    for r in retained:
        print(f"    {r}")
    print(f"\n  sentient species flagged: {len(sentient)}")
    for s in sentient:
        print(f"    {s}")
    print(f"\n  untagged (no biomes, held as lore): {len(untagged)}")
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
