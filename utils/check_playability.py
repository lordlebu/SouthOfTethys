"""Check that the authored world can actually be played through.

lint_story.py proves the JSON is well formed and every reference resolves. That is not the
same as the content working: a discovery can validate perfectly and still be unreachable
because the word it needs is only taught by someone whose line requires that same discovery.

This walks the world the way a player does and reports what cannot be reached:

  placement     every point of interest belongs to a field map that lists it, and back
  reachability  every discovery is findable somewhere, every NPC stands somewhere
  ladders       every rung's requirements can be satisfied BEFORE that rung -- see below
  words         every word is actually handed over by a line someone can say
  questions     every question is raised, and every reading of it can be reached
  entry         every gated sub-location opens for someone who did the work

**Making is the game's, not this file's** (2 October 2026). Materials, items, processes, recipes,
vehicles and homesteads moved to the game repository, which checks them there: what each map can
make (`test/criticalPath.test.ts`), the cook fire, and every id canon names that the game owns
(`test/gameOwned.test.ts`). This file used to mirror the game's making rules in Python and keep the
two in step by hand; that duplicate is what the move removed.

    python utils/check_playability.py
    python utils/check_playability.py field_map_lothal

Why this is a simulation rather than a set check
------------------------------------------------
The obvious implementation asks "is this requirement obtainable somewhere on the map?", and
that is what this script used to do. It passes a cycle: discovery A's last rung requires B,
B's last rung requires A, each is "obtainable somewhere", and neither can ever be first. That
shipped, and the game's own finishability test caught it rather than this.

So the check starts from nothing and repeatedly does whatever is now possible -- climb a rung,
hear a line, take a word -- until nothing more opens. Whatever is still unreached at the end is
genuinely unreachable, and the order it was authored in cannot hide it.

A duplicated rule, deliberately
-------------------------------
The two requirement readings below mirror `canAdvance` and `linesFor` in the game's
`src/journey.ts`. That is a second implementation of one rule and it is a real cost; it is
accepted because the alternative is authoring canon with no way to know it is playable until
it has been exported. If the game's semantics change, change them here too.
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
    out = {}
    for f in sorted(d.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        out[doc["id"]] = doc
    return out


class World:
    """Everything authored, indexed."""

    def __init__(self) -> None:
        self.maps = load_all("field_maps")
        self.pois = load_all("points_of_interest")
        self.discoveries = load_all("discoveries")
        self.questions = load_all("field_questions")
        self.npcs = load_all("npcs")
        self.happenings = load_all("happenings")
        # A person's arc (the owner's of 2 October 2026): who it brings, and what its beats grant.
        self.storylines = load_all("storylines")
        self.words = load_all("vocabulary")
        self.flora = load_all("flora")
        self.fauna = load_all("fauna")
        self.regions = load_all("regions")
        biomes = json.loads((DB / "biomes.json").read_text(encoding="utf-8")).get("biomes") or []
        self.renderable = {b["id"] for b in biomes if b.get("renderable")}

    def last_rung(self, did: str) -> int:
        return len(self.discoveries[did].get("levels") or []) - 1


class State:
    """How far a notional player has got. Mirrors `Progress` in the game."""

    def __init__(self) -> None:
        self.rungs: dict[str, int] = {}
        self.words: set[str] = set()
        self.questions: set[str] = set()

    def rung_of(self, did: str) -> int:
        return self.rungs.get(did, -1)


def holds(w: World, s: State, req: str) -> bool:
    """Understood. What climbing a rung and entering a place both ask for."""
    if req.startswith("word_"):
        return req in s.words
    if req not in w.discoveries:
        return False
    return s.rung_of(req) >= w.last_rung(req)


def observed(w: World, s: State, req: str) -> bool:
    """Seen closely enough to reason from. What a line and a reading ask for."""
    if req.startswith("word_"):
        return req in s.words
    if req not in w.discoveries:
        return False
    return s.rung_of(req) >= 1


def play(w: World, here: set[str]) -> State:
    """Start from nothing and do whatever becomes possible, until nothing more does.

    A rung waits on nothing but understanding (the owner's ruling, 2 October 2026): no hour, no
    weather and no tool in hand, so the ladder alone is the whole question.
    """
    s = State()
    people = {n for p in here for n in (w.pois[p].get("npcs") or [])}
    findable = {d for d, doc in w.discoveries.items() if here & set(doc.get("found_at") or [])}

    # Questions a place raises simply by being stood in.
    for q, doc in w.questions.items():
        if doc.get("raised_at") in here:
            s.questions.add(q)

    changed = True
    while changed:
        changed = False

        # Look at things. A discovery is climbable if it can be found here, or if somebody
        # has already pointed it out.
        for did in findable | set(s.rungs):
            levels = w.discoveries[did].get("levels") or []
            while True:
                nxt = s.rung_of(did) + 1
                if nxt >= len(levels):
                    break
                if not all(holds(w, s, r) for r in levels[nxt].get("requires") or []):
                    break
                s.rungs[did] = nxt
                changed = True

        # Talk to people. Lines are the only thing that hands over a word.
        for nid in sorted(people):
            for line in w.npcs[nid].get("lines") or []:
                if not all(observed(w, s, r) for r in line.get("requires") or []):
                    continue
                for gift in line.get("gives") or []:
                    if gift in w.words and gift not in s.words:
                        s.words.add(gift)
                        changed = True
                    elif gift in w.questions and gift not in s.questions:
                        s.questions.add(gift)
                        changed = True
                    elif gift in w.discoveries and did_notice(s, gift):
                        changed = True

        # Things that happen to you. A written happening wins over a woven one whenever it can
        # happen and is never rationed, so once its map is walked and what it asks for has been
        # seen, it happens: its choices are as sure a source as a line. Every choice, because
        # every choice is takeable -- the game offers the last one even when all are gated.
        for hid in sorted(w.happenings):
            h = w.happenings[hid]
            if not can_happen_here(w, h, here):
                continue
            if not all(observed(w, s, r) for r in h.get("requires") or []):
                continue
            for choice in h.get("choices") or []:
                for gift in choice.get("grants") or []:
                    if gift in w.words and gift not in s.words:
                        s.words.add(gift)
                        changed = True
                    elif gift in w.questions and gift not in s.questions:
                        s.questions.add(gift)
                        changed = True
                    elif gift in w.discoveries and did_notice(s, gift):
                        changed = True
    return s


def can_happen_here(w: World, h: dict, here: set[str]) -> bool:
    """Whether some point in `here` is somewhere this happening can find the traveller.

    `at` narrows an arrival to its points of interest; otherwise any point on one of its maps
    will do, and no maps means every map. Mirrors `canHappen` in the game's `events.ts`.
    """
    maps = set(h.get("field_maps") or [])
    at = set(h.get("at") or [])
    for p in here:
        if maps and w.pois[p].get("field_map") not in maps:
            continue
        if at and p not in at:
            continue
        return True
    return False


def did_notice(s: State, did: str) -> bool:
    """Being told about something puts it at rung 0. Returns whether that was news."""
    if s.rung_of(did) >= 0:
        return False
    s.rungs[did] = 0
    return True


def why_stuck(w: World, s: State, did: str) -> str:
    """The requirement that never arrived, for a message worth reading."""
    levels = w.discoveries[did].get("levels") or []
    nxt = s.rung_of(did) + 1
    if nxt >= len(levels):
        return "nothing -- it finished"
    rung = levels[nxt]
    missing = [r for r in rung.get("requires") or [] if not holds(w, s, r)]
    if missing:
        return f"rung {nxt} still needs {', '.join(sorted(missing))}"
    return f"rung {nxt} was never begun"


def structural(w: World, problems: list[str]) -> None:
    """The checks that do not need a simulation: things pointing at each other correctly."""
    for map_id, fm in w.maps.items():
        listed = set(fm.get("points_of_interest") or [])
        actual = {p for p, d in w.pois.items() if d.get("field_map") == map_id}
        for p in sorted(listed - actual):
            problems.append(f"{map_id} lists {p}, which does not point back at it")
        for p in sorted(actual - listed):
            problems.append(f"{p} claims {map_id}, which does not list it")

        for other in fm.get("neighbours") or []:
            if other not in w.maps:
                problems.append(f"{map_id} neighbours {other}, which does not exist")
            elif map_id not in (w.maps[other].get("neighbours") or []):
                problems.append(f"{map_id} neighbours {other}, which does not name it back")

        here = actual
        for p in sorted(here):
            for d in w.pois[p].get("discoveries") or []:
                if p not in (w.discoveries.get(d, {}).get("found_at") or []):
                    problems.append(f"{d} is listed on {p} but its own found_at does not agree")
            for n in w.pois[p].get("npcs") or []:
                if p not in (w.npcs.get(n, {}).get("found_at") or []):
                    problems.append(f"{n} is listed on {p} but its own found_at does not agree")

    for d, doc in w.discoveries.items():
        if not doc.get("found_at"):
            problems.append(f"{d} is not findable anywhere")
        for who in doc.get("helps") or []:
            if who not in w.npcs:
                problems.append(f"{d} helps {who}, who does not exist")

    brought = {sl.get("person") for sl in w.storylines.values()}
    for n, doc in w.npcs.items():
        # Somebody met only through their storyline stands nowhere on purpose: the arc brings them.
        # So does somebody who drives a craft on its round: they are met on it (`drives`).
        if not doc.get("found_at") and n not in brought and not doc.get("drives"):
            problems.append(f"{n} stands nowhere")

    for q, doc in w.questions.items():
        if not any(r.get("sound") for r in doc.get("resolutions") or []):
            problems.append(f"{q} has no sound resolution -- the player cannot be right")

    # A happening's `at` is an arrival, on its own maps. Either mistake makes it never happen,
    # and nothing else would say so: the game would simply never find the circumstance.
    grantable = set(w.discoveries) | set(w.words) | set(w.questions)
    for h, doc in sorted(w.happenings.items()):
        maps = set(doc.get("field_maps") or [])
        for p in doc.get("at") or []:
            if doc.get("occasion") != "arriving":
                problems.append(f"{h} names `at` {p}, but only an arrival happens at a point")
            if p not in w.pois:
                problems.append(f"{h} happens at {p}, which does not exist")
            elif maps and w.pois[p].get("field_map") not in maps:
                problems.append(f"{h} happens at {p}, which is not on any of its field_maps")
        for m in maps - set(w.maps):
            problems.append(f"{h} happens on {m}, which does not exist")
        for choice in doc.get("choices") or []:
            for g in choice.get("grants") or []:
                # A recipe is the game's now: it checks that one resolves (`test/gameOwned.test.ts`).
                if g not in grantable and not g.startswith("recipe_"):
                    problems.append(
                        f"{h} grants {g}, which is not a discovery, word, question or recipe "
                        "-- a happening opens what a line opens, and nothing else"
                    )


def main() -> int:
    w = World()
    only = sys.argv[1] if len(sys.argv) > 1 else None

    problems: list[str] = []
    structural(w, problems)

    # The truth for a player is the whole connected world: they can travel. Per-map figures
    # come after, and are reported rather than enforced -- a map that needs its neighbour is
    # a design choice, not a fault.
    everywhere = set(w.pois)
    if only:
        everywhere = {p for p, d in w.pois.items() if d.get("field_map") == only}

    end = play(w, everywhere)

    for did in sorted(w.discoveries):
        if not (set(w.discoveries[did].get("found_at") or []) & everywhere):
            continue
        if end.rung_of(did) < w.last_rung(did):
            problems.append(f"{did} cannot be finished: {why_stuck(w, end, did)}")

    for word in sorted(w.words):
        if word in end.words:
            continue
        givers = [n for n, d in w.npcs.items()
                  for line in (d.get("lines") or []) if word in (line.get("gives") or [])]
        if not givers:
            problems.append(f"{word} is declared but no line hands it over")
        else:
            problems.append(f"{word} is only given by {', '.join(sorted(set(givers)))}, "
                            "whose line can never be said")

    for q, doc in w.questions.items():
        if doc.get("raised_at") and doc["raised_at"] not in everywhere:
            continue
        if q not in end.questions:
            problems.append(f"{q} is never raised -- nobody asks it and nowhere prompts it")
        for i, r in enumerate(doc.get("resolutions") or []):
            missing = [x for x in r.get("requires") or [] if not observed(w, end, x)]
            if missing:
                problems.append(f"{q} reading {i} needs {', '.join(sorted(missing))}, "
                                "which is never got")

    for p in sorted(everywhere):
        for sub in w.pois[p].get("sub_locations") or []:
            missing = [r for r in sub.get("requires") or [] if not holds(w, end, r)]
            if missing:
                problems.append(f"{p}/{sub['id']} needs {', '.join(sorted(missing))}, "
                                "which is never got")

    for map_id, fm in sorted(w.maps.items()):
        if only and map_id != only:
            continue
        here = {p for p, d in w.pois.items() if d.get("field_map") == map_id}
        local = play(w, here)
        claimed = {d for d, doc in w.discoveries.items() if here & set(doc.get("found_at") or [])}
        finished = [d for d in claimed if local.rung_of(d) >= w.last_rung(d)]
        print(f"  {map_id}")
        print(f"    points of interest : {len(here)}")
        print(f"    discoveries        : {len(claimed)}")
        print(f"    people             : {len({n for p in here for n in (w.pois[p].get('npcs') or [])})}")
        print(f"    words got here     : {len(local.words)}")
        print(f"    finishable alone   : {len(finished)} of {len(claimed)}")

    print()
    if problems:
        for p in problems:
            print(f"  UNREACHABLE  {p}")
        print(f"\n{len(problems)} problem(s)")
        return 1
    print("Playable: everything authored can be reached, in an order that exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
