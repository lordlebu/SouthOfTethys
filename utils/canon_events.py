"""Canon's events, in the order the story happens.

Kept beside `canon_epochs` and away from either generator, because the ordering bug this
project already had was *two copies of a sort that had drifted*. A third copy of the same
logic would be the same mistake with a different name.

Ordering is epoch first, from the declared table, then causally within the epoch. Canon
records no dates worth sorting on -- exactly one event in twelve carries a `date_approx` --
so the finest order canon actually knows is "which epoch" plus "what caused what". Anything
more precise would be invented here rather than read from canon.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canon_epochs import epoch_rank, rank_of

EVENTS_DIR = Path(__file__).resolve().parent.parent / "database" / "events"


def load_events() -> list[dict]:
    if not EVENTS_DIR.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(EVENTS_DIR.glob("*.json"))]


def ordered(events: list[dict], on_cycle=None) -> list[dict]:
    """Epoch order, then causal order inside the epoch, then id.

    Kahn's algorithm rather than networkx: twelve nodes do not justify a dependency, and the
    cycle detection that would be the real reason to reach for one falls out of the algorithm
    anyway -- anything still holding an indegree when the queue empties is in a cycle. Those
    are reported through `on_cycle` and appended rather than silently dropped, because an
    event vanishing from the timeline is a worse failure than one drawn in the wrong place.

    `lint_story.py` requires every edge to be stated from both ends, so the `successors` read
    here is the whole graph.
    """
    rank = epoch_rank()
    by_id = {e["id"]: e for e in events}

    indegree = {e["id"]: 0 for e in events}
    children: dict[str, list[str]] = {e["id"]: [] for e in events}
    for e in events:
        for succ in e.get("successors") or []:
            if succ in by_id:
                children[e["id"]].append(succ)
                indegree[succ] += 1

    def key(eid: str) -> tuple[int, str]:
        return (rank_of(by_id[eid].get("epoch"), rank), eid)

    ready = sorted([eid for eid, d in indegree.items() if d == 0], key=key)
    out: list[str] = []
    while ready:
        eid = ready.pop(0)
        out.append(eid)
        for child in children[eid]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort(key=key)

    cycled = sorted(set(by_id) - set(out))
    if cycled and on_cycle:
        on_cycle(cycled)
    out.extend(cycled)

    return [by_id[eid] for eid in out]
