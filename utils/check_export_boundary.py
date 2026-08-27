"""Prove that a lore change cannot reach the game by accident.

Canon is about to grow a great deal -- hundreds of places, across six epochs -- and almost
none of it is meant to ship. The thing standing between "canon grew" and "the game changed"
is one allowlist in `export_canon_bundle.py`, and an allowlist only works while somebody
remembers it exists.

Four checks, all of them cheap:

  boundary     every folder in database/ is explicitly exported or explicitly not.
               A new folder in neither is an error, so silence is not an option -- which is
               the whole point, because the natural way to add `place` is to create the
               folder and never think about the exporter again.

  fingerprint  the bundle the exporter would write still hashes to what canon expects.
               A lore edit that moves a byte in the game's data shows up here as a failure
               with the folder named, rather than as somebody's save file behaving oddly
               three weeks later.

  drift        if the game repository is sitting next to this one, its committed bundle is
               compared too. Skipped in CI, where it is not checked out.

  retrieval    every folder is also named in the indexer's DB_FOLDERS, or listed here as
               deliberately unindexed. Canon has three hardcoded folder allowlists -- BUNDLE,
               NOT_EXPORTED, and the indexer's -- and a folder missing from one of them fails
               silently in a different way each time. The indexer's has already cost this
               project once: its own comment records two field maps, twelve places, eighteen
               discoveries and both constructed languages sitting invisible to retrieval
               because nobody updated a list.

`canon_version` is not sufficient for any of this. The case that proved it: `main` and
`feat/flora-growth-forms` both declared 1.11.0 while producing a different `species.json`,
and it was the branch's copy that sat committed in the game. A version nobody bumps
identifies nothing. Hashes do.

    python utils/check_export_boundary.py            # verify
    python utils/check_export_boundary.py --update   # re-pin, deliberately
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_canon_bundle import BUNDLE, DB, DEFAULT_OUT, NOT_EXPORTED, build_bundle, render

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
FINGERPRINT = DB / "export.lock.json"

# Directories under database/ that are not canon content and so are not the exporter's
# business either. `schemas` validates canon rather than being it.
NOT_CONTENT = {"schemas"}

# Folders the retrieval indexer deliberately skips. `timeline` holds the epoch table, which is
# a lookup rather than prose -- six rows of name and range that answer no question a person
# would ask the service. Listed rather than merely absent, which is the whole point.
NOT_INDEXED = {"timeline"}

INDEXER = BASE / "services" / "chroma" / "index_chroma_service.py"


def content_folders() -> list[str]:
    """Every directory under database/ that holds canon, in sorted order."""
    return sorted(
        d.name
        for d in DB.iterdir()
        if d.is_dir() and d.name not in NOT_CONTENT and any(d.glob("*.json"))
    )


def check_boundary() -> list[str]:
    """Every content folder is on exactly one side of the export boundary."""
    errors: list[str] = []
    exported = {folder for folders in BUNDLE.values() for folder in folders}
    withheld = set(NOT_EXPORTED)

    both = sorted(exported & withheld)
    for folder in both:
        errors.append(
            f"'{folder}' is in both BUNDLE and NOT_EXPORTED -- the exporter would ship it "
            f"while claiming it does not"
        )

    for folder in content_folders():
        if folder not in exported and folder not in withheld:
            errors.append(
                f"'database/{folder}/' is in neither BUNDLE nor NOT_EXPORTED. Add it to one "
                f"in utils/export_canon_bundle.py -- a folder that is quiet about which side "
                f"of the boundary it sits on is how lore reaches the game by accident"
            )

    # The reverse: an allowlist naming a folder nobody has created yet is a typo that
    # silently exports nothing, which reads as "that data was empty" rather than as a bug.
    on_disk = set(content_folders())
    for folder in sorted(exported - on_disk):
        errors.append(f"BUNDLE names 'database/{folder}/', which does not exist")

    return errors


def indexed_folders() -> list[str] | None:
    """The indexer's DB_FOLDERS, read without importing it.

    That module raises SystemExit at import when chromadb is absent, and chromadb is not in
    requirements.txt -- so `story-validation.yml`, which is the check this guard runs in,
    could never import it. Parsing the assignment is the way to read a list from a module you
    are deliberately not loading.
    """
    if not INDEXER.exists():
        return None
    tree = ast.parse(INDEXER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "DB_FOLDERS" for t in node.targets
        ):
            try:
                return list(ast.literal_eval(node.value))
            except ValueError:
                return None
    return None


def check_indexer() -> list[str]:
    """Every content folder is indexed, or is on the record as deliberately not."""
    listed = indexed_folders()
    if listed is None:
        return [
            f"could not read DB_FOLDERS from {INDEXER.relative_to(BASE)} -- the retrieval "
            f"index cannot be checked, which is how it silently went stale before"
        ]

    errors: list[str] = []
    known = set(listed) | NOT_INDEXED
    for folder in content_folders():
        if folder not in known:
            errors.append(
                f"'database/{folder}/' is not in the indexer's DB_FOLDERS and is not listed as "
                f"deliberately unindexed. It would be invisible to retrieval, and the deploy's "
                f"live-index check compares chunk count against every entity in index.json -- "
                f"so this also fails that check on main, permanently"
            )
    for folder in sorted(set(listed) - set(content_folders())):
        errors.append(f"the indexer names 'database/{folder}/', which does not exist")
    return errors


def fingerprint_of(files: dict[str, str]) -> dict[str, str]:
    return {
        name: hashlib.sha256(text.encode("utf-8")).hexdigest()
        for name, text in sorted(files.items())
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--update",
        action="store_true",
        help="re-pin the fingerprint to whatever canon produces now",
    )
    args = ap.parse_args()

    errors = check_boundary() + check_indexer()

    files, counts = build_bundle()
    current = fingerprint_of(files)

    if args.update:
        FINGERPRINT.write_text(
            render(
                {
                    "description": (
                        "What canon's exported surface hashes to. Written by "
                        "utils/check_export_boundary.py --update, and updated deliberately "
                        "when a lore change is meant to reach the game."
                    ),
                    "counts": counts,
                    "sha256": current,
                }
            ),
            encoding="utf-8",
        )
        print(f"Re-pinned {FINGERPRINT.relative_to(BASE)}")
        for name, digest in current.items():
            print(f"  {name:20} {digest[:16]}…")
        return 0

    if not FINGERPRINT.exists():
        errors.append(
            f"{FINGERPRINT.relative_to(BASE)} does not exist. Run with --update to create it."
        )
        expected = {}
    else:
        expected = json.loads(FINGERPRINT.read_text(encoding="utf-8")).get("sha256", {})

    for name in sorted(set(expected) | set(current)):
        if expected.get(name) != current.get(name):
            if name not in expected:
                errors.append(f"{name}: the bundle gained a file canon has not pinned")
            elif name not in current:
                errors.append(f"{name}: canon pins a file the bundle no longer produces")
            else:
                errors.append(
                    f"{name}: the exported bytes changed. If that was intended, re-pin with "
                    f"`python utils/check_export_boundary.py --update` and say so in the commit"
                )

    # --- drift against the game, when it is here ---------------------------------
    #
    # Not an error, and never in CI: the game is a sibling checkout that GitHub Actions does
    # not have. But when it is present this is the single most useful line in the output,
    # because it is the one that catches a bundle exported from a branch that never merged.
    drift: list[str] = []
    if DEFAULT_OUT.exists():
        for name, text in sorted(files.items()):
            target = DEFAULT_OUT / name
            if not target.exists():
                drift.append(f"{name}: not in the game's data/canon/")
                continue
            committed = target.read_text(encoding="utf-8")
            if committed.replace("\r\n", "\n") != text:
                drift.append(f"{name}: the game's committed copy differs from this canon")

    listed = indexed_folders() or []
    print(f"  folders    : {len(content_folders())} classified")
    print(f"  indexed    : {len(set(listed) & set(content_folders()))} of {len(content_folders())}"
          f" ({len(NOT_INDEXED)} deliberately not)")
    print(f"  entities   : {sum(counts.values())} exported")
    print(f"  fingerprint: {'pinned' if FINGERPRINT.exists() else 'MISSING'}")
    if DEFAULT_OUT.exists():
        print(f"  game bundle: {'matches' if not drift else str(len(drift)) + ' file(s) differ'}")
    else:
        print("  game bundle: not checked out, skipped")

    for d in drift:
        print(f"  DRIFT {d}")
    if drift:
        print(
            "\n  Drift is not a failure here -- canon does not own the game's working tree.\n"
            "  It means somebody exported from a different canon than this one."
        )

    if errors:
        for e in errors:
            print(f"  FAIL  {e}")
        print(f"\nExport boundary failed: {len(errors)} error(s)")
        return 1

    print("\nExport boundary holds: every folder is classified and the bundle is unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
