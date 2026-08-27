"""The epoch table, read from canon instead of restated in a script.

Both timeline generators used to carry their own copy of the epoch order, as a dict keyed on
`"civilization_dawn"`, `"migrations"` and so on. Every event in canon spells those ids
`"epoch_civilization_dawn"`. So every lookup missed, fell through to the `99` default, and the
tiebreak -- alphabetical by id -- became the only sort that ran. The rendered graph opened on
the Aravali Massacre and put Deep Antiquity eighth, for as long as anyone had been looking at
it. Both copies had also drifted from `epochs.json` in the same direction: each named an
`age_of_vanaras` that is not declared, and neither knew about `epoch_prehistoric`.

One copy, derived from the table itself, is the fix. Adding an epoch is now a data change.
"""

from __future__ import annotations

import json
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "database"
EPOCHS_PATH = DB / "timeline" / "epochs.json"

# An id the table does not declare sorts after everything it does, rather than silently
# tying with every other unknown at position zero.
UNPLACED = 10**6


def load_epochs() -> list[dict]:
    """The declared epochs, in the order canon states them -- which is chronological."""
    if not EPOCHS_PATH.exists():
        return []
    doc = json.loads(EPOCHS_PATH.read_text(encoding="utf-8"))
    return doc if isinstance(doc, list) else doc.get("epochs", [])


def epoch_rank() -> dict[str, int]:
    """Epoch id -> position, from the table's declared `order`.

    Falls back to array position for an epoch that has not been given one, so the table
    stays readable if somebody appends an entry and forgets.
    """
    return {e["id"]: e.get("order", i) for i, e in enumerate(load_epochs()) if "id" in e}


def epoch_ids() -> list[str]:
    """Every declared epoch id, in chronological order."""
    return [e["id"] for e in sorted(load_epochs(), key=lambda e: e.get("order", 0)) if "id" in e]


# Fields that say which era an entity belongs to. `epoch` is singular on characters and
# events; `epochs` is a list everywhere else; `epoch_founded` is a settlement stating when it
# began rather than when it existed, and is deliberately *not* a presence claim -- Lothal was
# founded in Civilization Dawn and is still standing, half-buried, after the Shattering.
PRESENCE_FIELDS = ("epoch", "epochs")


def declared_epochs(payload: dict) -> list[str]:
    """The epochs an entity claims, from whichever spelling it uses."""
    out: list[str] = []
    for field in PRESENCE_FIELDS:
        value = payload.get(field)
        if isinstance(value, str) and value:
            out.append(value)
        elif isinstance(value, list):
            out.extend(v for v in value if isinstance(v, str) and v)
    return out


def in_era(payload: dict, epoch_id: str) -> bool:
    """Is this entity present in that era?

    **An entity that names no epoch is present in every era.** Silence means timeless, not
    unplaced -- which is what fauna already meant. 346 of the 363 entities carrying no epoch
    are species, and that was a deliberate call: a crocodile is not an era-specific thing.
    Reading silence as "unplaced" would have required dating all 346 before any of them could
    appear in an atlas. Ruling recorded in DESIGN.md, 2026-08-27.
    """
    claimed = declared_epochs(payload)
    return epoch_id in claimed if claimed else True


def state_in_era(payload: dict, epoch_id: str) -> dict:
    """An entity as it stands in one era.

    A place states its identity once and overrides only what changed -- Dwarka is a working
    harbour in Civilization Dawn and a drowned gate after the Shattering, at the same
    coordinates. Most entities carry no `states` at all and come back untouched.
    """
    merged = {k: v for k, v in payload.items() if k != "states"}
    for state in payload.get("states") or []:
        if state.get("epoch") == epoch_id:
            merged.update({k: v for k, v in state.items() if k != "epoch"})
    return merged


def rank_of(epoch_id: str | None, rank: dict[str, int] | None = None) -> int:
    if rank is None:
        rank = epoch_rank()
    return rank.get(epoch_id or "", UNPLACED)
