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
  conditions    no rung waits on weather the world never produces
  making        every recipe can actually be performed, and every item can be got

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

# Weather the schema allows that `world/weather.ts` deliberately never generates: one is a
# phase of the moon, the other a state of the land. A rung gated on either can never be
# climbed. See docs/decisions.md.
UNPRODUCED_WEATHER = {"full_moon", "flood"}


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
        self.words = load_all("vocabulary")
        self.materials = load_all("materials")
        self.items = load_all("items")
        self.processes = load_all("processes")
        self.recipes = load_all("recipes")

    def classes_of(self, mid: str) -> set[str]:
        return set(self.materials.get(mid, {}).get("classes") or [])

    def affords(self, iid: str) -> set[str]:
        """What an item lets you do, following base_item up the chain.

        Inheritance is read here rather than resolved at export, because the checker has to
        agree with whatever the game will compute -- and the game reads the same chain. An
        item that overrides `affords` replaces its base's rather than adding to it, which is
        how Factorio's override works and is the less surprising of the two readings.
        """
        seen, cursor = set(), iid
        while cursor and cursor not in seen:
            seen.add(cursor)
            doc = self.items.get(cursor) or {}
            if doc.get("affords"):
                return set(doc["affords"])
            cursor = doc.get("base_item")
        return set()

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
    """Start from nothing and do whatever becomes possible, until nothing more does."""
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
    return s


def did_notice(s: State, did: str) -> bool:
    """Being told about something puts it at rung 0. Returns whether that was news."""
    if s.rung_of(did) >= 0:
        return False
    s.rungs[did] = 0
    return True


def make(w: World, biomes: set[str], kinds: set[str]) -> tuple[set[str], set[str]]:
    """Start from what the ground offers and make whatever becomes possible.

    The same shape as `play` above and for the same reason. The naive question -- "does a
    recipe exist for this item?" -- passes a chain that can never start: a rope whose recipe
    needs a loom, and a loom whose recipe needs a rope. Both exist, both name real
    ingredients, and neither can ever be first. Asking instead "what can be made from
    nothing, and then from that" is the only formulation that finds it.

    That exact cycle was in the first draft of these recipes. Spinning was written as needing
    the `work` affordance, which only a loom, a quern or a bow-drill provides, and every one
    of those needs cordage. Nothing in the fibre half of canon could be made at all.

    Returns the materials and items obtainable, given the biomes a map is made of and the
    kinds of place standing on it.
    """
    held_m = {
        mid for mid, doc in w.materials.items()
        if biomes & set(doc.get("found_in") or [])
    }
    held_i: set[str] = set()

    changed = True
    while changed:
        changed = False
        have_classes = {c for m in held_m for c in w.classes_of(m)}
        have_affords = {a for i in held_i for a in w.affords(i)}

        for rid, r in sorted(w.recipes.items()):
            proc = w.processes.get(r.get("process"), {})

            # Where it must happen. Absent means anywhere, including standing in a field.
            at = set(proc.get("performed_at") or [])
            if at and not (at & kinds):
                continue

            # What the maker must be holding -- an affordance, not a named tool.
            if not set(proc.get("needs") or []) <= have_affords:
                continue

            ok = True
            for need in r.get("ingredients") or []:
                if "tag" in need and need["tag"].lstrip("#") not in have_classes:
                    ok = False
                elif "material" in need and need["material"] not in held_m:
                    ok = False
                elif "item" in need and need["item"] not in held_i:
                    ok = False
                if not ok:
                    break
            if not ok:
                continue

            for got in r.get("outputs") or []:
                if "item" in got and got["item"] not in held_i:
                    held_i.add(got["item"])
                    changed = True
                elif "material" in got and got["material"] not in held_m:
                    held_m.add(got["material"])
                    changed = True

    return held_m, held_i


def making(w: World, problems: list[str]) -> None:
    """Every recipe is performable somewhere, and every item can be got somewhere.

    Judged across the whole authored world rather than per map, because a player travels: a
    recipe that only works at Dwarka is fine, and one that works nowhere is a bug.
    """
    if not w.recipes:
        return

    biomes = {b for fm in w.maps.values() for b in (fm.get("seed_biomes") or [])}
    kinds = {d.get("kind") for d in w.pois.values() if d.get("kind")}
    held_m, held_i = make(w, biomes, kinds)

    for rid, r in sorted(w.recipes.items()):
        outs = [o.get("item") or o.get("material") for o in r.get("outputs") or []]
        if any(o in held_i or o in held_m for o in outs):
            continue
        proc = w.processes.get(r.get("process"), {})
        at = set(proc.get("performed_at") or [])
        if at and not (at & kinds):
            problems.append(
                f"{rid} is performed at {'/'.join(sorted(at))}, and no point of interest "
                f"on any map is one"
            )
            continue
        missing_tools = set(proc.get("needs") or []) - {a for i in held_i for a in w.affords(i)}
        if missing_tools:
            problems.append(
                f"{rid} needs something that {'/'.join(sorted(missing_tools))}s, and nothing "
                f"obtainable does"
            )
            continue
        short = []
        for need in r.get("ingredients") or []:
            if "tag" in need and need["tag"].lstrip("#") not in {
                c for m in held_m for c in w.classes_of(m)
            }:
                short.append(need["tag"])
            elif "material" in need and need["material"] not in held_m:
                short.append(need["material"])
            elif "item" in need and need["item"] not in held_i:
                short.append(need["item"])
        problems.append(f"{rid} can never be performed: nothing supplies {', '.join(short)}")

    # An item nothing yields and no recipe makes. A prototype is exempt -- it exists to be
    # inherited from, not to be held, which is why `item_cordage` has no recipe and should not.
    prototypes = {d["base_item"] for d in w.items.values() if d.get("base_item")}
    for iid in sorted(w.items):
        if iid in held_i or iid in prototypes:
            continue
        problems.append(f"{iid} exists but nothing gathers or makes it")

    for mid in sorted(w.materials):
        if mid in held_m:
            continue
        problems.append(
            f"{mid} exists but is found in no map's biomes and no recipe produces it"
        )


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
        for lvl_i, lvl in enumerate(doc.get("levels") or []):
            bad = set((lvl.get("conditions") or {}).get("weather") or []) & UNPRODUCED_WEATHER
            if bad and not set((lvl.get("conditions") or {}).get("weather") or []) - bad:
                problems.append(
                    f"{d} rung {lvl_i} waits on {', '.join(sorted(bad))}, which the world "
                    "never produces (see docs/decisions.md)"
                )

    for n, doc in w.npcs.items():
        if not doc.get("found_at"):
            problems.append(f"{n} stands nowhere")

    for q, doc in w.questions.items():
        if not any(r.get("sound") for r in doc.get("resolutions") or []):
            problems.append(f"{q} has no sound resolution -- the player cannot be right")


def main() -> int:
    w = World()
    only = sys.argv[1] if len(sys.argv) > 1 else None

    problems: list[str] = []
    structural(w, problems)
    making(w, problems)

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
