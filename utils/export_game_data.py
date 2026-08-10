"""Export canon species to 4000BCESaraswathy's data/creatures.json and data/flora.json.

Phase 2 of the canon/game integration. database/ owns the species canon; the game
consumes a generated projection of it. This replaces the game's own
tools/build-species-data.js, which read docs/bestiary.md directly and made the game
repo a second entity store for the same fiction.

The output shape is dictated by src/world/types.ts. It is not validated here -- the
game imports the JSON and `npm run typecheck` is the check, which is stricter than
anything this script could assert about itself.

Two things about the output are load-bearing:

  order   `pickFor` indexes into the per-biome list, so array order decides which
          creature a given tile shows. It is part of the seed contract. Entities carry
          `source_index` recording the authored bestiary sequence; anything without one
          (species authored in canon, absent from the bestiary) sorts after, by id, so
          adding canon entities can never reshuffle the existing ones.

  format  2-space indent, trailing newline, non-ASCII left unescaped -- matching
          JSON.stringify(value, null, 2) so diffs against the old generator stay
          readable. Several species names carry diacritics ("Maya-born"), so
          ensure_ascii would rewrite every one of them.

Also writes data/canon.lock.json: the canon version and a hash of each exported file,
so the game's CI can tell that its committed data still matches a known canon release
rather than having been hand-edited.

    python utils/export_game_data.py                 # dry run, reports the diff
    python utils/export_game_data.py --apply
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path(os.environ.get("CANON_REPO", REPO.parent / "4000BCESaraswathy")) / "data"

# Field order matters only for diff readability, but a stable order keeps the file from
# churning. This is the order the previous generator emitted.
FAUNA_FIELDS = ["id", "name", "binomial", "region", "biomes", "placement", "rarity", "mood", "journalPrompt"]
FLORA_FIELDS = [f for f in FAUNA_FIELDS if f != "mood"]

# Sorts after every bestiary entry, so canon-only species append rather than interleave.
UNINDEXED = 10**9


def game_id(canon_id: str) -> str:
    return canon_id.split("_", 1)[1].replace("_", "-")


def region_lookup() -> dict[str, str]:
    """canon region id -> bestiary region slug, for entities that predate the import."""
    out = {}
    for f in sorted((REPO / "database" / "regions").glob("*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        if "bestiary_region" in payload:
            out[payload["id"]] = payload["bestiary_region"]
    return out


def to_game(entity: dict, kind: str, regions: dict[str, str]) -> dict:
    region = entity.get("region")
    if not region:
        # Authored in canon rather than imported: recover a region from its habitats.
        for habitat in entity.get("habitats") or []:
            if habitat in regions:
                region = regions[habitat]
                break
    out = {
        "id": game_id(entity["id"]),
        "name": entity["name"],
        "binomial": entity.get("scientific") or None,
        "region": region or "canon",
        "biomes": entity.get("biomes") or [],
        "placement": entity.get("placement") or "lore",
        "rarity": entity.get("rarity") or "common",
        # `notes` is the canon reference fact and `journal_prompt` the player-facing
        # prose; they are deliberately separate fields. Entities authored in canon have
        # only the former, and are all placement "lore" so the player never reads this.
        "journalPrompt": entity.get("journal_prompt") or entity.get("notes") or "",
    }
    if kind == "fauna":
        out["mood"] = entity.get("mood") or "watchful"
    fields = FAUNA_FIELDS if kind == "fauna" else FLORA_FIELDS
    return {f: out[f] for f in fields}


def collect(kind: str, regions: dict[str, str]) -> list[dict]:
    entities = [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted((REPO / "database" / kind).glob("*.json"))
    ]
    entities.sort(key=lambda e: (e.get("source_index", UNINDEXED), e["id"]))
    return [to_game(e, kind, regions) for e in entities]


def render(rows: list[dict]) -> str:
    return json.dumps(rows, indent=2, ensure_ascii=False) + "\n"


# The lock file's hashes are defined over LF-normalised content. Without this, Python's
# newline translation writes CRLF on Windows while the hash was taken on LF, so the
# freshness check fails on exactly the machine that generated the file.
def write_lf(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def read_lf(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="the game's data/ directory (env CANON_REPO overrides the repo root)")
    ap.add_argument("--apply", action="store_true", help="write files; otherwise dry run")
    args = ap.parse_args()

    if not args.out.is_dir():
        print(f"ERROR: no such directory: {args.out}", file=sys.stderr)
        return 1

    index = json.loads((REPO / "database" / "index.json").read_text(encoding="utf-8"))
    regions = region_lookup()

    outputs = {"creatures.json": collect("fauna", regions), "flora.json": collect("flora", regions)}
    lock = {"canon_version": index["version"], "counts": {}, "sha256": {}}

    print("APPLIED" if args.apply else "DRY RUN — nothing written")
    for filename, rows in outputs.items():
        text = render(rows)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        lock["counts"][filename] = len(rows)
        lock["sha256"][filename] = digest

        target = args.out / filename
        before = read_lf(target) if target.exists() else None
        state = "unchanged" if before == text else ("new" if before is None else "CHANGED")
        print(f"  {filename:16} {len(rows):4} entries  {digest[:16]}  {state}")
        if args.apply:
            write_lf(target, text)

    if args.apply:
        write_lf(args.out / "canon.lock.json", json.dumps(lock, indent=2, ensure_ascii=False) + "\n")
    print(f"  canon version {lock['canon_version']}")
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
