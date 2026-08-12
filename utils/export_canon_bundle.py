"""Export canon in canon's own shape, for the game to adapt.

The previous exporter emitted `Creature` and `Flora` records -- the game's exact field list,
in the game's field order, reproduced by a Python script in this repo. That put the coupling
the wrong way round: canon could not gain a field, or a whole entity type, without an edit
here to teach it the game's data model. And it discarded everything that was not a species,
so the 441 entities in database/ reached the game as 346 flat rows.

This emits what canon actually holds, and leaves the shaping to the side that owns the
engine. Canon changes when the fiction changes; the game changes when the design does.

Four files rather than one, split by what a module needs rather than by entity type:

  species.json      fauna and flora, with everything they carry
  places.json       regions, field maps, points of interest, the people standing in them,
                    and the biome vocabulary
  knowledge.json    discoveries, field questions, vocabulary

Plus canon.lock.json, which carries the version and a hash of each so the game's CI can
tell its committed copy still matches a canon release rather than having been hand-edited.

    python utils/export_canon_bundle.py            # dry run
    python utils/export_canon_bundle.py --apply
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB = REPO / "database"
DEFAULT_OUT = Path(os.environ.get("CANON_REPO", REPO.parent / "4000BCESaraswathy")) / "data" / "canon"

# Which folders land in which file. Ordering inside a file follows `source_index` where the
# entity has one, then id -- see the note on ordering below.
BUNDLE = {
    "species.json": ["fauna", "flora"],
    "places.json": ["regions", "field_maps", "points_of_interest", "npcs"],
    "knowledge.json": ["discoveries", "field_questions", "vocabulary"],
}

# Not exported: characters, events, settlements, factions, artifacts, mythology and the epoch
# table. They were 46 KB of the bundle and nothing in the game imported them -- Vite inlines
# every byte into the page, so an unused collection is weight on every load rather than
# something quietly available. They come back the day something reads them; the canon book and
# the retrieval service read `database/` directly and never wanted this file.
NOT_EXPORTED = ["characters", "events", "settlements", "factions", "artifacts", "mythology"]

# Sorts after every entity that has a source_index, so canon-only additions append.
UNINDEXED = 10**9


def load_folder(folder: str) -> list[dict]:
    d = DB / folder
    if not d.exists():
        return []
    entities = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("*.json"))]
    # Array order decides which species pickFor lands on for a tile, so it is part of the
    # seed contract rather than presentation. Entities carry source_index recording the
    # authored sequence; anything without one sorts after, by id, so additions never
    # reshuffle what came before.
    entities.sort(key=lambda e: (e.get("source_index", UNINDEXED), e.get("id", "")))
    return entities


def render(payload: dict) -> str:
    # 2-space indent, trailing newline, non-ASCII left alone -- several species names carry
    # diacritics, and ensure_ascii would rewrite every one of them.
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_lf(path: Path, text: str) -> None:
    # Hashes are taken over LF. Python's newline translation writes CRLF on Windows, so
    # without this the freshness check fails on the machine that generated the file.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_lf(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="the game's data/canon directory (env CANON_REPO overrides the repo root)")
    ap.add_argument("--apply", action="store_true", help="write files; otherwise dry run")
    args = ap.parse_args()

    index = json.loads((DB / "index.json").read_text(encoding="utf-8"))
    biomes = json.loads((DB / "biomes.json").read_text(encoding="utf-8"))
    files: dict[str, str] = {}
    counts: dict[str, int] = {}

    for filename, folders in BUNDLE.items():
        payload: dict = {"canon_version": index["version"]}
        for folder in folders:
            payload[folder] = load_folder(folder)
            counts[folder] = len(payload[folder])
        # The biome vocabulary belongs with places: it is what `seed_biomes` and `terrain`
        # are drawn from, and the game needs to know which of them it can render.
        if filename == "places.json":
            payload["biomes"] = biomes["biomes"]
        files[filename] = render(payload)

    lock = {
        "canon_version": index["version"],
        "counts": counts,
        "sha256": {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in files.items()},
    }
    files["canon.lock.json"] = render(lock)

    print("APPLIED" if args.apply else "DRY RUN — nothing written")
    for name, text in files.items():
        target = args.out / name
        before = read_lf(target) if target.exists() else None
        state = "unchanged" if before == text else ("new" if before is None else "CHANGED")
        kb = len(text.encode("utf-8")) / 1024
        print(f"  {name:20} {kb:7.1f} KB  {state}")
        if args.apply:
            write_lf(target, text)

    total = sum(len(t.encode("utf-8")) for t in files.values()) / 1024
    print(f"  {'total':20} {total:7.1f} KB   canon {lock['canon_version']}, {sum(counts.values())} entities")
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
