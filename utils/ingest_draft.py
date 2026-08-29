"""Read a drafted chapter and say what is wrong with it, before anything is written.

Four chapter documents were folded into canon by hand. Every one arrived *already
structured* -- the JSON was drafted, the prose was good, the cross-references pointed at each
other. And every one arrived wrong in ways that read as correct:

  invented epoch ids            4 of 4   `epoch_human_migrations` for `epoch_migrations`
  references to nothing         4 of 4   places, events and characters that do not exist
  duplicate of a real event     2 of 4   one leading article apart from canon's own
  `status` outside the enum     2 of 4   seven characters in a single document
  wrong id prefix               2 of 4   `myth_` where canon has `mythology_`
  a chain running backwards     1 of 4   Migrations naming Deep Antiquity as its successor
  entity type miscategorised    2 of 4   Owlman is a character, not a mythology

Not one of those needed a model to catch. Every one is mechanically checkable against canon,
and every one was caught by reading the schemas rather than the claim of compliance -- three of
the four documents stated they were "schema-compliant with all cross-references resolving".

So this is the reader, not the writer. Point it at the file:

    python utils/ingest_draft.py dump/my-chapter.md
    python utils/ingest_draft.py dump/my-chapter.md --apply    # write, if clean

`--apply` refuses while anything is wrong. A draft that half-lands is worse than one that does
not land at all, because the half that landed looks deliberate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canon_epochs import epoch_rank, load_epochs

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database"
SCHEMA_DIR = DB / "schemas"

# Reuse the linter's map rather than a second copy: the two drifting is the failure this
# repository keeps finding, and a folder listed in one and not the other is exactly that.
from lint_story import PREFIX_DIRS, SCHEMA_FOR  # noqa: E402

FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)
ID_SHAPED = re.compile("^(" + "|".join(re.escape(p) for p in PREFIX_DIRS) + ")[a-z0-9_]+$")
NOT_REFERENCES = {"sources", "type", "canon", "id"}


def canon() -> dict[str, dict]:
    found = {}
    for folder in set(PREFIX_DIRS.values()):
        d = DB / folder
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            p = json.loads(f.read_text(encoding="utf-8"))
            found[p.get("id", f.stem)] = p
    return found


def refs(node, key=None):
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in NOT_REFERENCES:
                yield from refs(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from refs(v, key)
    elif isinstance(node, str) and ID_SHAPED.match(node):
        yield node


# Titles a draft adds to a name that canon records bare. "Professor Onko" is `character_onko`
# with a job in front of it, and no id check can see that -- the draft proposed
# `character_professor_onko`, which collides with nothing.
HONORIFICS = ("professor ", "prof ", "prof. ", "dr ", "dr. ", "doctor ", "captain ", "capt ",
              "elder ", "lady ", "lord ", "the ", "a ", "an ")


def bare(name: str) -> str:
    """A name with any honorific and leading article stripped, for comparing people."""
    n = (name or "").strip().lower().rstrip(".")
    changed = True
    while changed:
        changed = False
        for h in HONORIFICS:
            if n.startswith(h):
                n, changed = n[len(h):], True
    return n


def loose(title: str) -> str:
    """Two events are not different because one has an article in front of it."""
    t = (title or "").strip().lower()
    for article in ("the ", "a ", "an "):
        if t.startswith(article):
            return t[len(article):]
    return t


def folder_for(entity_id: str) -> str | None:
    for prefix, folder in PREFIX_DIRS.items():
        if entity_id.startswith(prefix):
            return folder
    return None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("draft", type=Path, help="a markdown or json file holding drafted entities")
    ap.add_argument("--apply", action="store_true", help="write the entities, if nothing is wrong")
    args = ap.parse_args()

    if not args.draft.exists():
        print(f"No such file: {args.draft}")
        return 1

    text = args.draft.read_text(encoding="utf-8")
    blocks = FENCE.findall(text) if args.draft.suffix != ".json" else [text]

    from jsonschema import Draft7Validator

    known = canon()
    epochs = {e["id"] for e in load_epochs()}
    rank = epoch_rank()
    titles = {loose(p["title"]): eid for eid, p in known.items()
              if p.get("type") == "event" and p.get("title")}
    people = {}
    for eid, payload in known.items():
        if payload.get("name"):
            people.setdefault(folder_for(eid) or "", {}).setdefault(bare(payload["name"]), eid)
    cultures_path = DB / "cultures.json"
    cultures = ({c["id"] for c in json.loads(cultures_path.read_text(encoding="utf-8"))["cultures"]}
                if cultures_path.exists() else None)

    drafted: list[dict] = []
    problems: list[tuple[str, str]] = []

    for raw in blocks:
        try:
            drafted.append(json.loads(raw))
        except json.JSONDecodeError as e:
            problems.append(("(unparsed block)", f"not valid JSON -- {e}"))

    # Ids the draft itself introduces count as resolvable: a chapter may reference its own
    # new places, and demanding they already exist would reject every chapter.
    incoming = {d["id"] for d in drafted if "id" in d}

    print(f"{args.draft}  --  {len(drafted)} payload(s)\n")

    for d in drafted:
        eid = d.get("id", "(no id)")
        folder = folder_for(eid) if isinstance(eid, str) else None
        found: list[str] = []

        if not folder:
            found.append(f"id prefix is not one canon uses ({', '.join(sorted(PREFIX_DIRS))})")
        else:
            stem = SCHEMA_FOR.get(folder)
            sp = SCHEMA_DIR / f"{stem}.schema.json"
            if sp.exists():
                v = Draft7Validator(json.loads(sp.read_text(encoding="utf-8")))
                for err in sorted(v.iter_errors(d), key=lambda e: list(e.path)):
                    where = ".".join(str(x) for x in err.path) or "(root)"
                    found.append(f"{where}: {err.message[:96]}")

        if eid in known:
            found.append(f"already exists in canon -- writing this would overwrite {folder}/{eid}.json")

        for field in ("epoch",):
            val = d.get(field)
            if isinstance(val, str) and val and val not in epochs:
                found.append(f"{field} '{val}' is not a declared epoch ({', '.join(sorted(epochs))})")
        for val in d.get("epochs") or []:
            if val not in epochs:
                found.append(f"epochs names '{val}', which is not declared")

        for r in sorted(set(refs(d))):
            if r not in known and r not in incoming:
                found.append(f"references '{r}', which does not exist and is not in this draft")

        if folder and d.get("name"):
            twin = people.get(folder, {}).get(bare(d["name"]))
            if twin and twin != eid:
                found.append(
                    f"name {d['name']!r} is {twin} with an honorific or article in front of it "
                    f"-- one person, not two"
                )

        if cultures is not None and d.get("culture") and d["culture"] not in cultures:
            found.append(f"culture '{d['culture']}' is not declared in cultures.json")

        if d.get("type") == "event" and d.get("title"):
            twin = titles.get(loose(d["title"]))
            # Not against itself: re-running on an already-ingested draft would otherwise
            # report every event as its own duplicate, on top of the collision already said.
            if twin and twin != eid:
                found.append(
                    f"title duplicates canon's {twin} -- two events for one happening"
                )
            here = rank.get(d.get("epoch") or "", None)
            for succ in d.get("successors") or []:
                other = known.get(succ) or next((x for x in drafted if x.get("id") == succ), None)
                if other and here is not None:
                    there = rank.get(other.get("epoch") or "", None)
                    if there is not None and there < here:
                        found.append(
                            f"successor '{succ}' sits in an earlier epoch -- this edge runs "
                            f"backwards through time"
                        )

        status = "OK" if not found else f"{len(found)} problem(s)"
        print(f"  {eid:44s} {status}")
        for f in found:
            print(f"       {f}")
        problems += [(eid, f) for f in found]

    print()
    if problems:
        print(f"{len(problems)} problem(s) across {len({p[0] for p in problems})} payload(s).")
        print("Nothing written." if args.apply else "Run again with --apply once these are fixed.")
        return 1

    if not args.apply:
        print("Clean. Re-run with --apply to write these into database/.")
        return 0

    for d in drafted:
        path = DB / folder_for(d["id"]) / f"{d['id']}.json"
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(BASE)}")
    print("\nNow run:  python utils/update_index.py --bump minor && python utils/lint_story.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
