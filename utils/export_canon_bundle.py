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
    "crafting.json": ["materials", "items", "processes", "recipes", "vehicles"],
}

# Not exported: characters, events, settlements, factions, artifacts, mythology and the epoch
# table. They were 46 KB of the bundle and nothing in the game imported them -- Vite inlines
# every byte into the page, so an unused collection is weight on every load rather than
# something quietly available. They come back the day something reads them; the canon book and
# the retrieval service read `database/` directly and never wanted this file.
#
# `timeline` holds the epoch table, which this comment has always claimed was withheld while
# the list below did not mention it. It was withheld in fact -- nothing added it to BUNDLE --
# but by omission rather than by decision, which is not a thing to rely on as the lore layer
# grows. `check_export_boundary.py` now requires every folder to be named on one side.
#
# `places` is the lore layer: hundreds of named locations the player will never stand in.
# It is listed here in the commit that created the folder, which is the rule the boundary
# check exists to enforce -- a new entity type that says nothing about which side it sits on
# is how lore reaches the game by accident.
NOT_EXPORTED = [
    "characters", "events", "settlements", "factions", "artifacts", "mythology", "timeline",
    "places",
    # `foodways` is the cultural half of food -- whose a dish is, when it is eaten, what it
    # marks. The edible half is an `item` and ships; this does not, on the same split that
    # keeps `mythology` out. The one link across the boundary is `foodway.dish`, which names
    # an item that does ship.
    "foodways",
]

# Sorts after every entity that has a source_index, so canon-only additions append.
UNINDEXED = 10**9

# Provenance fields withheld from the making-layer collections.
#
# `canon` and `sources` say how firmly canon believes a thing and where it came from. They are
# for the canon book and the retrieval service, both of which read `database/` directly, and
# nothing in the game has ever read either -- `src/content/canon.ts` touches `notes` only as a
# fallback for `journal_prompt`, and the `sources` the UI renders come from the retrieval
# service, not from the bundle.
#
# This is a boundary decision rather than a shape one, which is the distinction the "canon
# exports canon's own shape" rule turns on: that rule exists to stop canon tracking the game's
# *data model* -- it is why the exporter no longer emits `Creature` records. Choosing which
# canon facts cross the boundary at all is what the exporter already does per folder with
# NOT_EXPORTED, and per value when it keeps only renderable biomes. This is the same kind of
# call one level finer.
#
# 18 KB on a 540 KB budget, which is what made it worth doing now rather than later.
#
# **Deliberately not applied to species, places or knowledge yet.** The same argument holds for
# all three and would save more, but those three already feed a game with 460 passing tests and
# a committed lock file, so that change belongs in a commit where those tests are being run.
WITHHELD_FROM_CRAFTING = ("canon", "sources")


def resolved_affordances(items: list[dict]) -> dict[str, list[str]]:
    """What each item affords, with `base_item` followed to the end of the chain.

    Emitted so the game can check its answer against canon's rather than merely agreeing by
    convention. This rule genuinely lives in two languages -- `World.affords` here and
    `affordsOf` in `src/content/making.ts` -- because canon has to prove a recipe performable
    before it exports, and the comment on both has always said "change one, change both".

    A comment is not a guard. This is: `test/makingMatters.test.ts` asserts its own resolution
    equals this map for every item, so the two implementations fail together instead of
    drifting apart quietly. About 2 KB, which is a cheap price for the one rule in this layer
    that is written down twice.

    An item that states `affords` **replaces** its base's rather than adding to it, which is
    how Factorio's override works and is what the TypeScript does.
    """
    by_id = {i["id"]: i for i in items}
    out: dict[str, list[str]] = {}
    for item in items:
        seen: set[str] = set()
        cursor = item["id"]
        found: list[str] = []
        while cursor and cursor not in seen:
            seen.add(cursor)
            doc = by_id.get(cursor) or {}
            if doc.get("affords"):
                found = list(doc["affords"])
                break
            cursor = doc.get("base_item")
        out[item["id"]] = found
    return out


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


def build_bundle() -> tuple[dict[str, str], dict[str, int]]:
    """Render every bundle file, in memory, without writing anything.

    Split out of `main` so `check_export_boundary.py` can rebuild exactly what the exporter
    *would* write and compare it against a pinned fingerprint. Two copies of this loop would
    drift, and a guard that has drifted from the thing it guards is worse than no guard at
    all -- it reports success about a bundle nobody is building any more.
    """
    index = json.loads((DB / "index.json").read_text(encoding="utf-8"))
    biomes = json.loads((DB / "biomes.json").read_text(encoding="utf-8"))
    files: dict[str, str] = {}
    counts: dict[str, int] = {}

    for filename, folders in BUNDLE.items():
        payload: dict = {"canon_version": index["version"]}
        for folder in folders:
            entities = load_folder(folder)
            if filename == "crafting.json":
                entities = [
                    {k: v for k, v in e.items() if k not in WITHHELD_FROM_CRAFTING}
                    for e in entities
                ]
            payload[folder] = entities
            counts[folder] = len(payload[folder])
        # The biome vocabulary belongs with places: it is what `seed_biomes` and `terrain`
        # are drawn from, and the game needs to know which of them it can render.
        if filename == "places.json":
            payload["biomes"] = biomes["biomes"]
        # Canon's own answer to the one rule the game reimplements. See `resolved_affordances`.
        if filename == "crafting.json":
            payload["conformance"] = {"affords": resolved_affordances(payload["items"])}
        files[filename] = render(payload)

    lock = {
        "canon_version": index["version"],
        "counts": counts,
        "sha256": {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in files.items()},
    }
    files["canon.lock.json"] = render(lock)
    return files, counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="the game's data/canon directory (env CANON_REPO overrides the repo root)")
    ap.add_argument("--apply", action="store_true", help="write files; otherwise dry run")
    args = ap.parse_args()

    files, counts = build_bundle()
    canon_version = json.loads(files["canon.lock.json"])["canon_version"]

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
    print(f"  {'total':20} {total:7.1f} KB   canon {canon_version}, {sum(counts.values())} entities")
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
