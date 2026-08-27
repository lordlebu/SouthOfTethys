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
    """Epoch id -> position, from the table's own array order."""
    return {e["id"]: i for i, e in enumerate(load_epochs()) if "id" in e}


def rank_of(epoch_id: str | None, rank: dict[str, int] | None = None) -> int:
    if rank is None:
        rank = epoch_rank()
    return rank.get(epoch_id or "", UNPLACED)
