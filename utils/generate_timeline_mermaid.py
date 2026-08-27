"""Draw canon's timeline: the epochs as a timeline, the events as a causal graph.

Two diagrams, because canon holds two different things and one picture cannot carry both.

  The epoch timeline is chronology. It comes from `timeline/epochs.json` and shows all six
  epochs including the three that hold no events yet -- Prehistoric, Current and
  Post-Cataclysm. Those empty bands are the authoring backlog made visible, and hiding them
  would make the diagram tidier and less true. Post-Cataclysm in particular is the era the
  game is set in.

  The event graph is causality. Edges come from `successors`, grouped into one subgraph per
  epoch so that the four events with no edges at all -- the Shadow Pact, the Dragon's Spine,
  the Aravali Massacre and the Naraka Portal -- still land in the right band. Before this,
  they floated as disconnected boxes with nothing saying they came first.

Mermaid is the right tool for both only because both stay small: six epochs, twelve events.
The geography view deliberately does not live here. Hundreds of places would make a graph
nothing can lay out and nobody can read; that is SVG's job.

Ordering comes from `canon_epochs`, and within an epoch from a topological sort of the events
themselves, so the picture follows the story rather than the alphabet.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canon_epochs import load_epochs
from canon_events import load_events, ordered

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent.parent
# See the note in generate_timeline.py: docs/ is the one tracked location, because the
# intermediate copy is precisely what went stale.
OUT_DIR = BASE / "docs"
OUT_MD = OUT_DIR / "timeline_mermaid.md"


def label(text: str) -> str:
    """Mermaid node text. Quotes end a label and brackets end a node."""
    return text.replace('"', "'").replace("[", "(").replace("]", ")")


def period(text: str) -> str:
    """Mermaid timeline text. A colon separates a period from its entries."""
    return text.replace(":", " --").strip()


def epoch_timeline(events: list[dict]) -> str:
    """All declared epochs, in canon's order, with the events that sit in each."""
    in_epoch: dict[str, list[dict]] = {}
    for e in events:
        in_epoch.setdefault(e.get("epoch") or "", []).append(e)

    lines = ["```mermaid", "timeline", "    title South of Tethys — the epochs"]
    for ep in load_epochs():
        lines.append(f"    section {period(ep.get('name') or ep['id'])}")
        entries = [period(e.get("title") or e["id"]) for e in in_epoch.get(ep["id"], [])]
        rng = period(ep.get("range") or "undated")
        if entries:
            lines.append(f"        {rng} : " + " : ".join(entries))
        else:
            # An epoch canon has declared and not yet populated. Saying so is the point.
            lines.append(f"        {rng} : (no events recorded yet)")
    lines.append("```")
    return "\n".join(lines)


def event_graph(events: list[dict]) -> str:
    """The causal DAG, banded by epoch."""
    node_of = {e["id"]: f"E{i}" for i, e in enumerate(events)}
    by_epoch: dict[str, list[dict]] = {}
    for e in events:
        by_epoch.setdefault(e.get("epoch") or "", []).append(e)

    lines = ["```mermaid", "graph TD"]

    # Empty epochs are skipped here, unlike in the timeline above: an empty subgraph draws as
    # a labelled box containing nothing, which reads as a rendering fault rather than as a
    # gap in the authoring. The timeline is where absence is stated.
    for ep in load_epochs():
        members = by_epoch.get(ep["id"], [])
        if not members:
            continue
        lines.append(f'    subgraph {ep["id"]}["{label(ep.get("name") or ep["id"])}"]')
        for e in members:
            lines.append(f'        {node_of[e["id"]]}["{label(e.get("title") or e["id"])}"]')
        lines.append("    end")

    stray = [e for e in events if (e.get("epoch") or "") not in {x["id"] for x in load_epochs()}]
    for e in stray:
        lines.append(f'    {node_of[e["id"]]}["{label(e.get("title") or e["id"])}"]')

    for e in events:
        for succ in e.get("successors") or []:
            if succ in node_of:
                lines.append(f'    {node_of[e["id"]]} --> {node_of[succ]}')

    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    def warn(cycled):
        print(f"  WARNING  {len(cycled)} event(s) in a cycle, appended unordered: "
              f"{', '.join(cycled)}")

    events = ordered(load_events(), on_cycle=warn)
    epochs = load_epochs()
    populated = {e.get("epoch") for e in events}

    doc = [
        "# The Timeline of South of Tethys",
        "",
        "_Generated from `database/events/` and `database/timeline/epochs.json` by"
        " `utils/generate_timeline_mermaid.py`. Do not edit by hand._",
        "",
        "## The epochs",
        "",
        epoch_timeline(events),
        "",
        "## The events, by cause",
        "",
        "Edges are `successors`. Events sit in the epoch they declare; an event with no edges"
        " is not adrift, it simply has no recorded cause or consequence yet.",
        "",
        event_graph(events),
        "",
    ]

    empty = [e for e in epochs if e["id"] not in populated]
    if empty:
        doc += [
            "## Epochs with no events yet",
            "",
            *(f"- **{e.get('name') or e['id']}** — {e.get('range') or 'undated'}" for e in empty),
            "",
        ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(doc), encoding="utf-8")
    print(f"✅ Mermaid → {OUT_MD.relative_to(BASE)}")
    print(f"   {len(events)} events, {len(epochs)} epochs, {len(empty)} of them empty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
