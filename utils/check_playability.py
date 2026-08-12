"""Check that a field map can actually be played through.

lint_story.py proves the JSON is well formed and every reference resolves. That is not the
same as the content working: a discovery can validate perfectly and still be unreachable
because the thing it requires is only taught by an NPC standing somewhere the player has no
reason to go.

This walks the slice the way a player would and reports what cannot be reached:

  placement     every point of interest belongs to a field map that lists it, and back
  reachability  every discovery is findable somewhere, every NPC stands somewhere
  ladders       every rung's requirements can be satisfied before that rung
  questions     every question has evidence that exists and at least one sound reading
  help          every `helps` names a real person, and they can actually be helped

    python utils/check_playability.py
    python utils/check_playability.py field_map_lothal
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "database"


def load_all(folder: str) -> dict[str, dict]:
    d = DB / folder
    if not d.exists():
        return {}
    return {json.loads(f.read_text(encoding="utf-8"))["id"]: json.loads(f.read_text(encoding="utf-8"))
            for f in sorted(d.glob("*.json"))}


def main() -> int:
    maps = load_all("field_maps")
    pois = load_all("points_of_interest")
    discoveries = load_all("discoveries")
    questions = load_all("field_questions")
    npcs = load_all("npcs")
    words = load_all("vocabulary")

    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only:
        maps = {k: v for k, v in maps.items() if k == only}

    problems: list[str] = []

    for map_id, fm in maps.items():
        listed = set(fm.get("points_of_interest") or [])
        actual = {p for p, d in pois.items() if d.get("field_map") == map_id}
        for p in sorted(listed - actual):
            problems.append(f"{map_id} lists {p}, which does not point back at it")
        for p in sorted(actual - listed):
            problems.append(f"{p} claims {map_id}, which does not list it")

        # what the player can reach on this map
        here = {p for p in actual}
        found_here = {d for p in here for d in (pois[p].get("discoveries") or [])}
        people_here = {n for p in here for n in (pois[p].get("npcs") or [])}

        # every discovery that says it is found here, and every one the map's POIs claim
        claimed = {d for d, doc in discoveries.items() if here & set(doc.get("found_at") or [])}
        for d in sorted(found_here - claimed):
            problems.append(f"{d} is listed on a point of interest but its own found_at does not agree")

        # what a player on this map can come to hold
        obtainable = set(claimed)
        for n in people_here:
            for line in npcs[n].get("lines") or []:
                obtainable |= set(line.get("gives") or [])
        for w, doc in words.items():
            if set(doc.get("learned_from") or []) & (here | people_here):
                obtainable.add(w)

        for d in sorted(claimed):
            doc = discoveries[d]
            for i, rung in enumerate(doc.get("levels") or []):
                for req in rung.get("requires") or []:
                    if req not in obtainable:
                        problems.append(f"{d} rung {i} needs {req}, which cannot be got on {map_id}")

        for p in sorted(here):
            for sub in pois[p].get("sub_locations") or []:
                for req in sub.get("requires") or []:
                    if req not in obtainable:
                        problems.append(f"{p}/{sub['id']} needs {req}, which cannot be got on {map_id}")

        for n in sorted(people_here):
            for line in npcs[n].get("lines") or []:
                for req in line.get("requires") or []:
                    if req not in obtainable:
                        problems.append(f"{n} has a line needing {req}, which cannot be got on {map_id}")

        # help has to be possible, not merely declared
        for d in sorted(claimed):
            doc = discoveries[d]
            for who in doc.get("helps") or []:
                if who not in npcs:
                    problems.append(f"{d} helps {who}, who does not exist")
                elif who not in people_here:
                    problems.append(f"{d} helps {who}, who cannot be met on {map_id}")
            if doc.get("helps") and len(doc.get("levels") or []) < 4:
                problems.append(f"{d} helps someone but has too few rungs to reach the actionable one")

        # questions
        for q, doc in questions.items():
            if doc.get("raised_at") not in here:
                continue
            for ev in doc.get("evidence") or []:
                if ev not in discoveries:
                    problems.append(f"{q} cites {ev}, which does not exist")
            if not any(r.get("sound") for r in doc.get("resolutions") or []):
                problems.append(f"{q} has no sound resolution -- the player cannot be right")
            for r in doc.get("resolutions") or []:
                for req in r.get("requires") or []:
                    if req not in obtainable:
                        problems.append(f"{q} has a reading needing {req}, which cannot be got on {map_id}")

        placed = {n for n in npcs if set(npcs[n].get("found_at") or []) & here}
        for n in sorted(people_here - placed):
            problems.append(f"{n} is listed on a point of interest but its own found_at does not agree")

        print(f"  {map_id}")
        print(f"    points of interest : {len(actual)}")
        print(f"    discoveries        : {len(claimed)}")
        print(f"    people             : {len(people_here)}")
        print(f"    obtainable here    : {len(obtainable)}")
        actionable = [d for d in claimed if len(discoveries[d].get('levels') or []) >= 7]
        print(f"    reach the last rung: {len(actionable)}")

    # anything authored but unreachable from any map
    for d, doc in discoveries.items():
        if not doc.get("found_at"):
            problems.append(f"{d} is not findable anywhere")
    for n, doc in npcs.items():
        if not doc.get("found_at"):
            problems.append(f"{n} stands nowhere")

    print()
    if problems:
        for p in problems:
            print(f"  UNREACHABLE  {p}")
        print(f"\n{len(problems)} problem(s)")
        return 1
    print("Playable: everything authored can be reached, and every question can be answered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
