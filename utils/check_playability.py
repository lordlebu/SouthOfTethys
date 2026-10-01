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
  finite        what never renews, and is concentrated in one kind of ground (reported)
  map by map    what each map can make with only its own ground, teachers and benches, read
                the way the game places species (gates; MAKING_PER_MAP_KEPT names what is kept)

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

# Which placements the game actually stands on a tile, by kind. Mirrors `species.ts`, which
# indexes fauna by `encounter` and flora by `flavour` -- and, from the Roads and Hands fix, flora
# by `encounter` too: twenty-seven plants were authored `encounter` and the game, reading only
# `flavour` for flora, never grew one, which left thirteen materials won from them dead. `lore` is
# never placed by either. Absent placement reads as `lore`, as the game's adapter reads it.
PLACED = {"fauna": {"encounter"}, "flora": {"flavour", "encounter"}}

# Ground the generator stamps on every map whatever its palette says. `landmark` is one tile --
# the journey's destination, put back after classification -- and no `seed_biomes` lists it,
# because it is a place rather than a climate. One tile is still ground: sandalwood stands there.
STAMPED_ON_EVERY_MAP = {"landmark"}

# **The per-map making report gates, and this is the one switch.**
#
# It measures what a traveller can make on one map with only that map's ground and that map's
# teachers. On the day it was written it found real gaps -- dried fish taught on a Lothal with no
# salt, ink and palm-leaf taught on a Narmada that cannot fire a pot -- and it was printed rather
# than enforced until Phase 1 of Roads and Hands had filled them in content (fibre cord, reed rope
# by hand, sea salt, Okhi's jar and awl). It was switched on in canon 2.41.0, when the report came
# out clean but for the one gap below that is kept on purpose; every other line it prints is a
# problem and the exit code follows.
MAKING_PER_MAP_GATES = True

# **Gaps kept on purpose, by map and recipe, each with its reason.** A ratchet in both directions,
# as the game's `test/criticalPath.test.ts` is: a gap not named here fails, and an entry here that no
# longer fails is reported stale, so this list can only be emptied deliberately.
MAKING_PER_MAP_KEPT: dict[tuple[str, str], str] = {
    # The princess's one task is to be cooked the Fourteen, and the Fourteen wants salt. The plateau
    # has none -- salt is the lowland's, and the Maru carry it up to trade -- so the traveller brings
    # it from the coast (Lothal's sea salt, Dwarka's crust) or brings the dish ready cooked. That is
    # what makes it a task rather than a recipe, and it is reachable world-wide. Root tea itself is
    # ginger and ashwagandha, both on the Narmada. Owner may overrule: a plateau rock salt would close it.
    ("field_map_narmada", "recipe_root_tea"): "the princess's price wants salt carried up to the plateau",
}


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
        self.homesteads = load_all("homesteads")
        self.words = load_all("vocabulary")
        self.materials = load_all("materials")
        self.items = load_all("items")
        self.processes = load_all("processes")
        self.recipes = load_all("recipes")
        self.flora = load_all("flora")
        self.fauna = load_all("fauna")
        self.regions = load_all("regions")
        biomes = json.loads((DB / "biomes.json").read_text(encoding="utf-8")).get("biomes") or []
        self.renderable = {b["id"] for b in biomes if b.get("renderable")}

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


def play(w: World, here: set[str], tools: set[str] | None = None,
         gettable: set[str] | None = None) -> State:
    """Start from nothing and do whatever becomes possible, until nothing more does.

    `tools` is the affordances the traveller can have by then, and `gettable` the items --
    both from the craft closure, because a rung that wants something which cuts is asking a
    question about the making layer and not about the ladder. Passing None means "assume
    anything", which is what a caller checking the ladders alone wants.

    **Canon does not model the starting kit.** That is the game's fact -- canon says what
    exists in the world, the game says what the traveller brought. It costs nothing here:
    all four kit pieces have recipes, so the closure reaches them like anything else.
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


def make(w: World, biomes: set[str], kinds: set[str], ground: set[str] | None = None,
         knows=None) -> tuple[set[str], set[str]]:
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

    `ground` and `knows` are the per-map report's two narrowings, and both default to the
    world-wide reading the gates above have always used. `ground` replaces "any material whose
    `found_in` meets these biomes" with an answer already worked out -- `ground_of`, which knows
    a material won from a plant comes only from where that plant is placed. `knows(rid, items)`
    says whether a recipe has been taught by now; it is handed the items held so far because a
    teacher can charge one, and the price may be something this very loop has to make first.
    """
    if ground is not None:
        held_m = set(ground)
    else:
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
            if knows is not None and not knows(rid, held_i):
                continue
            proc = w.processes.get(r.get("process"), {})

            # Where it must happen. Absent means anywhere, including standing in a field.
            at = set(proc.get("performed_at") or [])
            if at and not (at & kinds):
                continue

            # What the maker must be holding -- an affordance, not a named tool.
            if not set(proc.get("needs") or []) <= have_affords:
                continue

            # **Counts are ignored, deliberately, and it is a bargain with the game.**
            #
            # This asks whether an ingredient class can be obtained *at all*, never whether four
            # of it can. Canon could not answer the second question if it wanted to: `found_in`
            # says which biomes hold a material and nothing anywhere says how much of it there
            # is, because canon does not model a world's stock.
            #
            # It is sound only because the game's `gather` does not use a tile up -- walking
            # back gives the same reeds again, so there is no quantity a patient walker cannot
            # reach and "obtainable" and "obtainable four times" are one question. The day that
            # changes, this loop starts passing recipes nobody can afford and says nothing.
            # `test/makingMatters.test.ts` over there pins the no-depletion half so the
            # assumption cannot quietly stop being true.
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

    # A rung that wants a tool nothing can supply is unclimbable, and reads as a content bug
    # rather than a gap in the making layer unless it is named here.
    afforded = {a for i in held_i for a in w.affords(i)}
    for did, doc in sorted(w.discoveries.items()):
        for i, lvl in enumerate(doc.get("levels") or []):
            for need in lvl.get("needs_tool") or []:
                if need not in afforded:
                    problems.append(
                        f"{did} rung {i} needs something that {need}s, and nothing obtainable does"
                    )

    # `taught_by` is a claim about a person, and the person has to actually say it.
    #
    # Both directions, because unlike faction `members` -- which is one-directional precisely so
    # it cannot drift -- this edge genuinely has two ends that are authored separately: the
    # recipe names the teacher, and a line of theirs gives the recipe. Either half alone is a
    # bug, and they are opposite bugs. A recipe naming a teacher who never says it is
    # unlearnable. A line giving a recipe that names no teacher teaches nothing, because a
    # recipe without `taught_by` is common knowledge from the first step.
    for rid, r in sorted(w.recipes.items()):
        for who in r.get("taught_by") or []:
            if who not in w.npcs:
                problems.append(f"{rid} is taught by {who}, who does not exist")
                continue
            if not any(rid in (ln.get("gives") or []) for ln in w.npcs[who].get("lines") or []):
                problems.append(
                    f"{rid} says {who} teaches it, and no line of theirs gives it -- "
                    f"the recipe would be unlearnable"
                )
        givers = sorted({
            n for n, d in w.npcs.items()
            for ln in (d.get("lines") or []) if rid in (ln.get("gives") or [])
        })
        if givers and not r.get("taught_by"):
            problems.append(
                f"{rid} is given by {', '.join(givers)} but names no taught_by, so it is "
                f"already common knowledge and the line teaches nothing"
            )

    # A price nobody can pay.
    for nid, doc in sorted(w.npcs.items()):
        for i, line in enumerate(doc.get("lines") or []):
            price = line.get("costs")
            if price and price not in held_i:
                problems.append(f"{nid} line {i} costs {price}, which nothing gathers or makes")


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


def nothing_runs_out(w: World, problems: list[str], notes: list[str]) -> None:
    """Nothing a recipe needs can be used up beyond recovery.

    **This is the check that had to exist before the game could deplete anything**, and it is
    deliberately not the check that was planned. The plan said "teach the closure to count":
    multiply out every recipe's `count` and prove the world holds enough. Measuring first showed
    that would be almost entirely noise, and would miss the fault that actually reaches a player.

    Why counting is the wrong question. `make()` above ignores counts, and its own comment
    explains the bargain that makes it sound: the game's tiles are inexhaustible, so "obtainable"
    and "obtainable four times" are one question. Depletion breaks that -- but only partly.
    A material that regenerates is *still* inexhaustible to a patient walker; waiting is not
    running out. So `fast`, `seasonal` and `slow` keep the old bargain exactly, and the only
    thing that can strand somebody is `renews: never`.

    Why *this* question. Canon cannot count stock and should not try: `found_in` says which
    biomes hold a material and nothing says how much, because canon does not model a world's
    stock -- that is the game's, and it depends on a seed canon has never seen. What canon can
    see is the *shape* of a lock-out, which needs no simulation at all:

        a material that never renews,
        that a recipe needs,
        that a map offers in only one of its biomes,
        and that nothing can make more of.

    All four together mean a player on that map is drawing down a finite supply concentrated in
    one kind of ground, with no way back. Three of the four are already load-bearing elsewhere,
    so this reads canon rather than inventing a new claim about it.

    The fourth clause is why this is not a naive scarcity warning, and it was found by reading
    the recipes rather than assuming: **`recipe_smelt_copper` takes 2 native copper and returns
    3.** Smelting makes copper rather than spending it, so a material that looks scarce can be
    the one thing on the map that is not. A check that counted ingredients and ignored outputs
    would have reported it as the worst case on two maps.

    Reported rather than enforced, and that is the honest register: a single-biome material is a
    design choice today -- shilajit is *meant* to be rare -- and becomes a fault only once a node
    can be emptied. When phase 4 lands, the pin in the game's `test/makingMatters.test.ts` and
    this list have to be read together.
    """
    if not w.recipes or not w.maps:
        return

    # What a recipe can produce more of than it consumes. Net, because 2-in-3-out is a source.
    renewable_by_craft: set[str] = set()
    for r in w.recipes.values():
        spent: dict[str, int] = {}
        for need in r.get("ingredients") or []:
            if "material" in need:
                spent[need["material"]] = spent.get(need["material"], 0) + int(need.get("count", 1))
        for got in r.get("outputs") or []:
            mid = got.get("material")
            if mid and int(got.get("count", 1)) > spent.get(mid, 0):
                renewable_by_craft.add(mid)

    # What a recipe asks for by name, and the largest single ask, so the note can say the stake.
    wanted: dict[str, int] = {}
    for r in w.recipes.values():
        for need in r.get("ingredients") or []:
            mid = need.get("material")
            if mid:
                wanted[mid] = max(wanted.get(mid, 0), int(need.get("count", 1)))

    for mid, most in sorted(wanted.items()):
        doc = w.materials.get(mid) or {}
        if doc.get("renews") != "never" or mid in renewable_by_craft:
            continue
        found_in = set(doc.get("found_in") or [])
        if not found_in:
            continue

        for map_id, fm in sorted(w.maps.items()):
            here = found_in & set(fm.get("seed_biomes") or [])
            if len(here) != 1:
                continue
            notes.append(
                f"{map_id}: {mid} never renews, is wanted {most} at a time, and is only in "
                f"{here.pop()} -- a node that empties would strand it here"
            )


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

    # A happening's `at` is an arrival, on its own maps. Either mistake makes it never happen,
    # and nothing else would say so: the game would simply never find the circumstance.
    grantable = set(w.discoveries) | set(w.words) | set(w.questions) | set(w.recipes)
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
                if g not in grantable:
                    problems.append(
                        f"{h} grants {g}, which is not a discovery, word, question or recipe "
                        "-- a happening opens what a line opens, and nothing else"
                    )


def homesteads_hold(w: World, end: State, obtainable: set[str], problems: list[str]) -> None:
    """Every ground can be agreed and every stage built, by a player who has done what can be done.

    The settling loop is a chain of gates -- a worry answered, then another, then materials and
    people for each stage -- and a gate nothing opens stops the whole map's ending while every
    other check here stays green. So each worry needs at least one answer a player can reach: a
    discovery that can be finished, a person some finishable discovery helps, a word of the
    holder's tongue that some line hands over, a thing that can be gathered or made. And each
    stage's backers cannot outnumber the people of the map who can be helped.
    """
    finished = {d for d in w.discoveries if end.rung_of(d) >= w.last_rung(d)}
    helped = {who for d in finished for who in (w.discoveries[d].get("helps") or [])}
    for hid, doc in sorted(w.homesteads.items()):
        here = {p for p, d in w.pois.items() if d.get("field_map") == doc.get("field_map")}
        people = {n for n, d in w.npcs.items() if here & set(d.get("found_at") or [])}
        for g in doc.get("grounds") or []:
            language = (w.npcs.get(g.get("held_by")) or {}).get("language")
            for worry in g.get("worries") or []:
                def reachable(m: dict) -> bool:
                    kind = m.get("approach")
                    if kind == "show":
                        return m.get("discovery") in finished
                    if kind == "vouch":
                        return m.get("person") in helped
                    if kind == "tongue":
                        if m.get("word"):
                            return m["word"] in end.words
                        return any(x.startswith(f"word_{language}_") for x in end.words)
                    if kind == "offer":
                        return m.get("material") in obtainable
                    return False
                if not any(reachable(m) for m in worry.get("met_by") or []):
                    problems.append(f"{hid}: {g.get('id')}/{worry.get('id')} can never be answered")
        for stage in doc.get("stages") or []:
            for need in stage.get("needs") or []:
                if need.get("id") not in obtainable:
                    problems.append(f"{hid}: stage {stage.get('id')} needs {need.get('id')}, which can never be got")
            if stage.get("backers", 0) > len(people & helped):
                problems.append(
                    f"{hid}: stage {stage.get('id')} wants {stage['backers']} backers and only "
                    f"{len(people & helped)} people of the map can be helped"
                )


def map_biomes(fm: dict) -> set[str]:
    """The ground a map is made of: its palette, and what the generator stamps on every map."""
    return set(fm.get("seed_biomes") or []) | STAMPED_ON_EVERY_MAP


def map_lands(w: World, fm: dict) -> set[str]:
    """The landmasses a map reaches: its region's continent, and whatever its edges name.

    The same reading the lint's landmass rule takes. It is coarser than the game, which asks
    which landmass a *tile* is on -- the Aravali's north shore is Asia and its south shore is
    not -- so a species that lives only on one shore counts as placed on the whole map. That
    errs towards obtainable, which is the safe direction for a report that is not yet a gate.
    """
    lands = set((fm.get("landmass_edges") or {}).values())
    continent = (w.regions.get(fm.get("region") or "") or {}).get("continent")
    if continent:
        lands.add(continent)
    return lands


def placed_on(w: World, fm: dict) -> dict[str, set[str]]:
    """The species the game will actually stand on this map's tiles, and in which of its biomes.

    Four things have to agree, and each is one the game checks: the placement is one it places
    (`PLACED`), the biome is one it can draw (`renderable` -- the adapter drops the rest, and a
    species left with none becomes `lore`), the biome is on this map, and the species lives on a
    landmass the map reaches (`livesOn` in the game's `landmass.ts`; no `landmasses` means
    anywhere).
    """
    biomes = map_biomes(fm)
    lands = map_lands(w, fm)
    out: dict[str, set[str]] = {}
    for kind, pool in (("fauna", w.fauna), ("flora", w.flora)):
        for sid, doc in pool.items():
            if doc.get("placement") not in PLACED[kind]:
                continue
            where = set(doc.get("biomes") or []) & w.renderable & biomes
            if not where:
                continue
            lives = doc.get("landmasses")
            if lives and not set(lives) & lands:
                continue
            out[sid] = where
    return out


def ground_of(w: World, fm: dict, standing: dict[str, set[str]] | None = None) -> set[str]:
    """What a map's tiles give up, by the rule the game's `yieldsAt` uses.

    **A material with a living source comes from that source; a material without one comes from
    the ground.** So rice is got where a rice plant is placed *and* rice is `found_in` that
    biome, and flint wherever flint is `found_in`. Neither is "anything whose `found_in` meets
    the map", which is what `make()` assumes when it is not told otherwise -- and that is the
    blind spot this replaces: a material won from a `lore` plant passed every gate here, and
    could not be picked up anywhere in the game.

    The three materials the lint lets outrun their source (salt crust, oyster shell, leviathan
    bone) are read the game's way too, which is strictly: from where the source stands. Their
    wider `found_in` is a claim the game does not act on.
    """
    biomes = map_biomes(fm)
    if standing is None:
        standing = placed_on(w, fm)
    out: set[str] = set()
    for mid, doc in w.materials.items():
        found = set(doc.get("found_in") or []) & biomes
        sources = doc.get("won_from") or []
        if not sources:
            if found:
                out.add(mid)
        elif any(found & standing.get(s, set()) for s in sources):
            out.add(mid)
    return out


def taught_here(w: World, here: set[str], s: State) -> dict[str, list[str | None]]:
    """Recipe to the prices of the lines on this ground that teach it, None for a free one.

    A line teaches only if it can be said here -- its `requires` observed by what this map alone
    lets a player see, the same reading `play` gives every other line. A happening that can find
    the traveller here teaches too, as it hands over a word. Mirrors `learnRecipe`, which is fed
    by both, in the game's `journey.ts`.
    """
    out: dict[str, list[str | None]] = {}
    people = {n for p in here for n in (w.pois[p].get("npcs") or [])}
    for nid in sorted(people):
        for line in w.npcs[nid].get("lines") or []:
            if not all(observed(w, s, r) for r in line.get("requires") or []):
                continue
            for gift in line.get("gives") or []:
                if gift in w.recipes:
                    out.setdefault(gift, []).append(line.get("costs"))
    for h in w.happenings.values():
        if not can_happen_here(w, h, here):
            continue
        if not all(observed(w, s, r) for r in h.get("requires") or []):
            continue
        for choice in h.get("choices") or []:
            for gift in choice.get("grants") or []:
                if gift in w.recipes:
                    out.setdefault(gift, []).append(None)
    return out


def making_per_map(w: World, only: str | None) -> tuple[list[str], list[str]]:
    """What can be made on each map with only that map -- its ground, its teachers, its benches.

    Returns the lines to print and the findings among them, so the caller can decide whether the
    findings are problems (see `MAKING_PER_MAP_GATES`).

    **Why per map, when `making` above deliberately judges the whole world.** A player travels,
    so a recipe that only works at Dwarka is not a bug -- and that is still the gate. But it was
    the whole of the making check, and it pooled every biome and every kind of place in the world
    and assumed every recipe known. Three things it could not see, all measured:

      * a recipe taught on a map where the thing it needs does not grow, which the player meets
        as a teacher handing over something they cannot do anything with;
      * a homestead stage that needs a material its own map never yields -- and a homestead is
        built *here*, by the people of here, so "obtainable on another map" is a weaker answer
        than it sounds;
      * a material won only from a species the game never places. Pooled, it looked obtainable.

    So this runs the same fixed point as `make()`, from nothing, narrowed three ways: the
    materials are `ground_of` this map, the recipes are the common ones plus whatever a line on
    this map can teach, and the benches are this map's kinds of place. Then it says why each
    taught recipe and each homestead stage that did not come out of the loop is stuck -- a
    missing material, a missing tool, a missing kind of place, or a source placed nowhere.
    """
    out: list[str] = []
    findings: list[str] = []

    # What the whole world's ground yields, by the game's rule. Anything outside it and outside
    # every recipe the world can perform is dead everywhere, and is said once, at the end, rather
    # than once per map.
    standing_by_map = {mid: placed_on(w, fm) for mid, fm in w.maps.items()}
    placed_anywhere = {s for st in standing_by_map.values() for s in st}
    world_ground = set().union(*(ground_of(w, fm, standing_by_map[mid])
                                 for mid, fm in w.maps.items())) if w.maps else set()
    world_kinds = {d.get("kind") for d in w.pois.values() if d.get("kind")}
    world_m, _world_i = make(w, set(), world_kinds, ground=world_ground)
    prototypes = {d["base_item"] for d in w.items.values() if d.get("base_item")}

    def makers(thing: str) -> list[str]:
        return sorted(rid for rid, r in w.recipes.items()
                      if any(thing in (o.get("item"), o.get("material")) for o in r.get("outputs") or []))

    def why_material_nowhere(mid: str) -> str:
        doc = w.materials.get(mid) or {}
        sources = doc.get("won_from") or []
        # Never gathered, only made -- purified kuchla names its plant but is got from a recipe --
        # so the recipe is the reason, not the plant.
        if not doc.get("found_in") and makers(mid):
            return f"never gathered, and {', '.join(makers(mid))} can never be performed"
        if sources:
            unplaced = [s for s in sources if s not in placed_anywhere]
            if len(unplaced) == len(sources):
                kinds = sorted({
                    (w.flora.get(s) or w.fauna.get(s) or {}).get("placement") or "unplaced"
                    for s in sources
                })
                return f"won only from {', '.join(sources)} ({'/'.join(kinds)}), placed nowhere"
            return (f"won from {', '.join(sorted(set(sources) - set(unplaced)))}, never standing "
                    f"in its own found_in ({', '.join(doc.get('found_in') or []) or 'none'})")
        if makers(mid):
            return f"no ground holds it, and {', '.join(makers(mid))} can never be performed"
        return f"found in {', '.join(doc.get('found_in') or []) or 'no biome'}, which no map has"

    for map_id, fm in sorted(w.maps.items()):
        if only and map_id != only:
            continue
        here = {p for p, d in w.pois.items() if d.get("field_map") == map_id}
        kinds = {w.pois[p].get("kind") for p in here if w.pois[p].get("kind")}
        biomes = map_biomes(fm)
        standing = standing_by_map[map_id]
        ground = ground_of(w, fm, standing)
        seen = play(w, here)
        taught = taught_here(w, here, seen)

        def knows(rid: str, items: set[str]) -> bool:
            if not w.recipes[rid].get("taught_by"):
                return True
            return any(c is None or c in items for c in taught.get(rid, ()))

        held_m, held_i = make(w, biomes, kinds, ground=ground, knows=knows)
        affords = {a for i in held_i for a in w.affords(i)}
        classes = {c for m in held_m for c in w.classes_of(m)}

        # The explanations recurse -- a pot needs grog needs a broken jar -- so each carries the
        # trail of recipes it came by, and stops three deep or on meeting itself again. Deeper
        # than that a line stops being readable; what is left is said in a word, and the full
        # cause is printed under its own recipe whenever that is one this map teaches.
        def via(thing: str, recipes: list[str], trail: tuple[str, ...]) -> str:
            # Follow a recipe this map knows, if any does: that is the one a player would try.
            known_here = [r for r in recipes if knows(r, held_i)]
            first = (known_here or recipes)[0]
            if not known_here and (len(trail) >= 3 or first in trail):
                return f"{thing} ({first} is not taught on this map)"
            if len(trail) >= 3 or any(r in trail for r in recipes):
                return f"{thing} (not made here)"
            return f"{thing} <- {first}: {'; '.join(blockers(first, trail + (first,)))}"

        def why_material(mid: str, trail: tuple[str, ...] = ()) -> str:
            if mid not in world_m:
                return f"{mid} (dead everywhere: {why_material_nowhere(mid)})"
            doc = w.materials.get(mid) or {}
            sources = doc.get("won_from") or []
            found = set(doc.get("found_in") or []) & biomes
            recipes = makers(mid)
            # Made rather than gathered: the reason is the recipe's, so say that instead.
            if recipes and not doc.get("found_in"):
                return via(mid, recipes, trail)
            if not found:
                where = f"lies in {', '.join(doc.get('found_in') or [])}, none here"
            elif sources:
                where = f"won from {', '.join(sources)}, none standing in this map's {', '.join(sorted(found))}"
            else:
                where = "unreachable here"
            if recipes:
                where += f"; {', '.join(recipes)} not made here"
            return f"{mid} ({where})"

        def why_item(iid: str, trail: tuple[str, ...]) -> str:
            recipes = makers(iid)
            if not recipes:
                return f"{iid} (nothing makes it)"
            return via(iid, recipes, trail)

        def why_tag(tag: str) -> str:
            cls = tag.lstrip("#")
            members = sorted(m for m in w.materials if cls in w.classes_of(m))
            if not members:
                return f"{tag} (no material in canon has that class)"
            return f"{tag} (nothing of that class here: {', '.join(why_material(m) for m in members)})"

        def blockers(rid: str, trail: tuple[str, ...] = ()) -> list[str]:
            r = w.recipes[rid]
            why: list[str] = []
            if not knows(rid, held_i):
                who = ", ".join(r.get("taught_by") or [])
                if rid in taught:
                    # Every line that teaches it here charges, and nothing it charges is held.
                    prices = sorted({c for c in taught[rid] if c})
                    why.append(f"taught here only for a price: {', '.join(why_item(p, trail) for p in prices)}")
                else:
                    why.append(f"not taught on this map (taught by {who})")
            proc = w.processes.get(r.get("process"), {})
            at = set(proc.get("performed_at") or [])
            if at and not at & kinds:
                why.append(f"must be done at a {'/'.join(sorted(at))}, and nothing here is one")
            for tool in sorted(set(proc.get("needs") or []) - affords):
                able = sorted(i for i in w.items if tool in w.affords(i) and i not in prototypes)
                if not able:
                    why.append(f"needs something that can {tool}, and nothing in canon does")
                else:
                    why.append(f"needs something that can {tool}: {why_item(able[0], trail)}"
                               + (f" (or {', '.join(able[1:])})" if able[1:] else ""))
            for need in r.get("ingredients") or []:
                if "tag" in need and need["tag"].lstrip("#") not in classes:
                    why.append(f"missing {why_tag(need['tag'])}")
                elif "material" in need and need["material"] not in held_m:
                    why.append(f"missing {why_material(need['material'], trail)}")
                elif "item" in need and need["item"] not in held_i:
                    why.append(f"missing {why_item(need['item'], trail)}")
            return why

        # At the fixed point a recipe with nothing blocking it is one the loop performed. Asked
        # this way rather than "is its output held", because an output can be held by another
        # route -- gathered, or made by a second recipe -- while this one stays impossible.
        def performable(rid: str) -> bool:
            return not blockers(rid, (rid,))

        people = {n for n, d in w.npcs.items() if here & set(d.get("found_at") or [])}
        teaches = sorted(rid for rid, r in w.recipes.items() if set(r.get("taught_by") or []) & people)
        common = [rid for rid, r in w.recipes.items() if not r.get("taught_by")]
        known = [rid for rid in w.recipes if knows(rid, held_i)]

        local: list[str] = []
        kept: list[str] = []
        for rid in teaches:
            why = blockers(rid, (rid,))
            if why:
                line = (f"{rid} (taught by {', '.join(sorted(set(w.recipes[rid]['taught_by']) & people))}) "
                        f"cannot be made here: {'; '.join(why)}")
                if (map_id, rid) in MAKING_PER_MAP_KEPT:
                    kept.append(f"{line} -- kept: {MAKING_PER_MAP_KEPT[(map_id, rid)]}")
                else:
                    local.append(line)
            elif (map_id, rid) in MAKING_PER_MAP_KEPT:
                local.append(f"{rid} is in MAKING_PER_MAP_KEPT but can be made here now -- strike it off")
        for (kept_map, kept_rid) in MAKING_PER_MAP_KEPT:
            if kept_map == map_id and kept_rid not in teaches:
                local.append(f"{kept_rid} is in MAKING_PER_MAP_KEPT but nobody here teaches it -- strike it off")

        for hid, doc in sorted(w.homesteads.items()):
            if doc.get("field_map") != map_id:
                continue
            for stage in doc.get("stages") or []:
                for need in stage.get("needs") or []:
                    nid = need.get("id") or ""
                    if nid in held_m or nid in held_i:
                        continue
                    reason = why_item(nid, ()) if nid in w.items else why_material(nid)
                    local.append(f"{hid}: stage {stage.get('id')} needs {reason}")

        out.append(f"  {map_id}")
        out.append(f"    from the ground    : {len(ground)} materials ({len(held_m)} with making)")
        out.append(f"    recipes known      : {len(known)} ({len(common)} common, "
                   f"{len(known) - len(common)} taught here)")
        out.append(f"    recipes performable: {sum(1 for rid in w.recipes if performable(rid))}")
        out.append(f"    items makeable     : {len(held_i)}")
        for line in kept:
            out.append(f"    KEPT    {line}")
        for line in local:
            out.append(f"    CANNOT  {line}")
        findings.extend(f"{map_id}: {line}" for line in local)

    # Dead everywhere: no placed species and no ground yields it, and no recipe the whole world can
    # perform makes it. Said once, because every map would say it.
    if not only:
        dead = sorted(m for m in w.materials if m not in world_m)
        out.append("")
        out.append(f"  Yielded by no placed species, no ground, and no performable recipe: {len(dead)}")
        for mid in dead:
            out.append(f"    DEAD  {mid}: {why_material_nowhere(mid)}")
        findings.extend(f"{mid} can be got nowhere: {why_material_nowhere(mid)}" for mid in dead)

    return out, findings


def main() -> int:
    w = World()
    only = sys.argv[1] if len(sys.argv) > 1 else None

    problems: list[str] = []
    # Reported, never enforced. See `nothing_runs_out` -- these are design facts today and
    # become faults only once a resource node can be emptied.
    notes: list[str] = []
    structural(w, problems)
    making(w, problems)
    nothing_runs_out(w, problems, notes)

    # The truth for a player is the whole connected world: they can travel. Per-map figures
    # come after, and are reported rather than enforced -- a map that needs its neighbour is
    # a design choice, not a fault.
    everywhere = set(w.pois)
    if only:
        everywhere = {p for p, d in w.pois.items() if d.get("field_map") == only}

    # What the making layer can supply, handed to the walk. Without this a rung gated on a
    # tool would be judged reachable because the ladder allows it, which is exactly the kind of
    # "obtainable somewhere" answer this file exists to refuse.
    biomes = {b for fm in w.maps.values() for b in (fm.get("seed_biomes") or [])}
    kinds = {d.get("kind") for d in w.pois.values() if d.get("kind")}
    _materials, gettable = make(w, biomes, kinds)
    tools = {a for i in gettable for a in w.affords(i)}

    end = play(w, everywhere, tools, gettable)
    homesteads_hold(w, end, _materials | gettable, problems)

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
        local = play(w, here, tools, gettable)
        claimed = {d for d, doc in w.discoveries.items() if here & set(doc.get("found_at") or [])}
        finished = [d for d in claimed if local.rung_of(d) >= w.last_rung(d)]
        print(f"  {map_id}")
        print(f"    points of interest : {len(here)}")
        print(f"    discoveries        : {len(claimed)}")
        print(f"    people             : {len({n for p in here for n in (w.pois[p].get('npcs') or [])})}")
        print(f"    words got here     : {len(local.words)}")
        print(f"    finishable alone   : {len(finished)} of {len(claimed)}")

    if notes:
        print()
        print("  Finite, and concentrated in one kind of ground:")
        for n in notes:
            print(f"    {n}")

    # Making, map by map. Printed whatever happens; a problem only once `MAKING_PER_MAP_GATES`
    # is flipped, which is the whole of turning it into a gate.
    report, findings = making_per_map(w, only)
    print()
    print("  Making, map by map -- each map's own ground, teachers and benches"
          + ("" if MAKING_PER_MAP_GATES else " (reported, not yet enforced):"))
    for line in report:
        print(line)
    if MAKING_PER_MAP_GATES:
        problems.extend(findings)

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
