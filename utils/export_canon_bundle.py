"""Export canon in canon's own shape, for the game to adapt.

The previous exporter emitted `Creature` and `Flora` records -- the game's exact field list,
in the game's field order, reproduced by a Python script in this repo. That put the coupling
the wrong way round: canon could not gain a field, or a whole entity type, without an edit
here to teach it the game's data model. And it discarded everything that was not a species,
so the 441 entities in database/ reached the game as 346 flat rows.

This emits what canon actually holds, and leaves the shaping to the side that owns the
engine. Canon changes when the fiction changes; the game changes when the design does.

Three files rather than one, split by what a module needs rather than by entity type:

  species.json      fauna and flora, with everything they carry
  places.json       regions, field maps, points of interest, the people standing in them,
                    what can happen to you there, what is said on the road between them,
                    and the biome vocabulary
  knowledge.json    discoveries, field questions, vocabulary

There was a fourth, `crafting.json`, and `homesteads` rode in `places.json`. Both left on 2 October
2026, when the owner moved making to the game: materials, items, processes, recipes, vehicles and
homesteads are the game's own data now, under its `data/making/`. Canon keeps the world's nouns.

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
    "places.json": ["regions", "field_maps", "points_of_interest", "npcs", "happenings",
                    # What the peoples say on the road, shown in the cutscenes. Placed here as
                    # `happenings` were, and for the same reason: a saying belongs to the maps and
                    # the journey between them -- its `field_maps` point at this file's maps -- and
                    # nothing in it is learned or held, which is what `knowledge.json` is for.
                    # `carried_by` is a bare culture id; the credit on screen is `attribution`.
                    "sayings",
                    # A person's arc, beat by beat (the owner's of 2 October 2026). Placed here as
                    # happenings are: its beats happen at this file's places, on this file's maps.
                    "storylines"],
    "knowledge.json": ["discoveries", "field_questions", "vocabulary"],
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
    # an item the game owns.
    "foodways",
]

# Sorts after every entity that has a source_index, so canon-only additions append.
UNINDEXED = 10**9

# Provenance fields withheld from every exported collection.
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
# It began on the making layer alone, saving 18 KB, with a note that the same argument held for
# species, places and knowledge and that applying it there belonged in a commit where the game's
# suite was being run alongside.
#
# **The budget gate is what collected on that note.** The Indian food batch took the bundle to
# 563.9 KB against a 560 KB limit, and the rule written beside that limit says the answer is a
# lore/play split inside the exported types rather than a bigger number. So this now applies to
# all four files, and gives back 60 KB -- appreciably more than the batch that forced it cost.
#
# **`epochs` joined them when two more homesteads took the bundle to 562.1 KB.** The game reads no
# epoch anywhere -- `src/` never names the field, and `test/adapterCoverage.test.ts` lists it as
# skipped on every collection -- because the whole game is set in one of them. About 7 KB across
# 146 entities. When the game grows a second era this comes back off the list, deliberately.
#
# **`appearance` joined them in the commit that created it.** It is what a species looks like, in
# prose for the books and the art plan's prompts -- a body, a colour, a texture. The game draws
# paintings and marks and has never read a description of how a thing looks, so every byte of it
# would be inlined into the page and read by nothing.
#
# **`inspired_by` joined them in the commit that created it.** A saying may be written after a
# real-world text -- a Rigvedic hymn -- and canon records that, with what the line is to it: an
# original composition, never a translation. That is provenance, the same kind of fact as
# `sources`, and the owner's ruling of 2026-10-01 is that the game credits a saying in-world only
# ("Vedda saying"). The lore portal shows it, from `database/`.
WITHHELD = ("canon", "sources", "epochs", "appearance", "inspired_by")

# `notes` as well, for the three folders whose notes nothing reads.
#
# **Per-folder rather than global, because `notes` is play content in half the bundle and
# authoring rationale in the other half.** `canon.ts` reads a species' notes as the fallback for
# `journal_prompt`, and `making.ts` reads them as the description of every material, item,
# process, recipe and vehicle -- five call sites. Adding `notes` to `WITHHELD` would silently
# blank all of those.
#
# The three below are the other half. The game's `Discovery`, `FieldQuestion` and `Word`
# interfaces in `src/content/knowledge.ts` have **no `notes` field at all**, so every byte was
# inlined into the page by Vite and read by nothing: 11.3 KB across 45 discoveries, 1.3 KB across
# 7 questions and 1.6 KB across 10 words.
#
# Checked the way `withhold_lore_species` was before it withheld anything -- by reading the
# consuming interfaces rather than by grepping for the word, because a field that is destructured
# would not show up as `.notes` anywhere.
#
# (`recipes` was the fourth, and `homesteads` was withheld from the commit that created it. Both
# moved to the game with the making layer on 2 October 2026, and left this list with it.)
#
# **`happenings` is the fifth, and was withheld from the commit that created it.** The game's
# `GameEvent` has no `notes`: a happening's `notes` are the authoring rationale -- which thesis it
# serves, why its grant opens nothing new -- and the prose the player reads is `prose`.
#
# **And the four folders of `places.json`, when happenings took the bundle to 558.9 KB.** The game's
# `RawFieldMap`, `RawPoi` and `RawNpc` in `src/content/places.ts` carry no `notes`, and its
# `CanonRegion` reads only `bestiary_region`; `test/adapterCoverage.test.ts` lists `notes` as skipped
# on all four. Checked by reading those interfaces and every importer of `places.json`, the way the
# first three were. About 30 KB of authoring rationale -- why a map was retired, whose line was
# moved where -- that no player ever saw. The player's prose on these is `description`, `arrival`
# and `lines`, and those stay.
WITHHELD_NOTES = (
    "discoveries", "field_questions", "vocabulary", "happenings",
    "regions", "field_maps", "points_of_interest", "npcs",
    # A saying's `notes` record what was changed from the owner's draft to fit canon -- a horse
    # made an ox, a line ungendered. Editing history; the player reads `text` and `attribution`.
    "sayings",
    # A storyline's `notes` are how the owner's outline was fitted; the player reads the beats.
    "storylines",
)


def withhold_lore_species(folder: str, entities: list[dict]) -> list[dict]:
    """Drop species the game can never place.

    `placement: lore` means "exists in the record alone" -- authored, real, and not something a
    player can meet. The game filters on that at load: `species.ts` indexes fauna by `encounter`
    and flora by `flavour`, so a `lore` entity is read, held in memory, and never chosen.

    **This is the lore/play split the budget rule asks for, applied one level finer.** Shipping
    them cost 25.5 KB across 35 entities and bought nothing: checked before withholding, no
    material's `won_from`, no recipe and no discovery names any of them, so nothing in the other
    three files is left pointing at a species that is no longer there.

    Withheld rather than deleted, and the distinction is the whole of the canon/game split.
    Canon is the record and keeps them; the bundle is what one game needs to draw a walk, and
    these are not part of that. It is the same call `NOT_EXPORTED` makes per folder.

    The day a sky mode places them, `placement` changes in canon and they cross the boundary
    again with no edit here -- which is exactly what just happened to sixteen of them.
    """
    if folder not in ("fauna", "flora"):
        return entities
    return [e for e in entities if e.get("placement") != "lore"]


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
    cultures = json.loads((DB / "cultures.json").read_text(encoding="utf-8"))
    files: dict[str, str] = {}
    counts: dict[str, int] = {}

    for filename, folders in BUNDLE.items():
        payload: dict = {"canon_version": index["version"]}
        for folder in folders:
            entities = load_folder(folder)
            entities = withhold_lore_species(folder, entities)
            drop = WITHHELD + (("notes",) if folder in WITHHELD_NOTES else ())
            entities = [{k: v for k, v in e.items() if k not in drop} for e in entities]
            payload[folder] = entities
            counts[folder] = len(payload[folder])
        # The biome vocabulary belongs with places: it is what `seed_biomes` and `terrain`
        # are drawn from, and the game needs to know which of them it can render.
        if filename == "places.json":
            payload["biomes"] = biomes["biomes"]
            # The peoples a stranger can belong to, with the names they give their children. Only
            # cultures that carry `given_names` cross: the other two dozen are lore the game never
            # reads, and the bundle budget is a lore/play split.
            payload["peoples"] = [
                {"id": c["id"], "given_names": c["given_names"]}
                for c in cultures["cultures"]
                if c.get("given_names")
            ]
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
