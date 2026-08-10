"""A small HTTP seam between the canon and the game.

The two repos have only ever shared data: the game is a static bundle with canon baked
in at build time, and it makes no network calls at all. That is still true by default --
this service is additive, and the game degrades to exactly its current behaviour when
nothing is listening.

What it adds is the thing the walk cannot do from a static file: ask canon a question
about the place you are standing in, and have the Vidur model write about it.

Two endpoints rather than one, because they cost wildly different amounts:

  POST /lore   retrieval only. Milliseconds once the collection is warm, and useful on
               its own -- it answers "what does canon actually say about this?" with
               entity ids you can go read.
  POST /ask    retrieval plus generation. Seconds, and it loads a causal LM on first
               call. The game treats a passage as a bonus, never as something it waits
               on before drawing.

Run it:

    pip install -r services/api/requirements.txt
    CHROMA_PERSIST_DIR=storage/chroma uvicorn services.api.main:app --port 8000 --reload
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

REPO = Path(__file__).resolve().parents[2]
# The retrieval and generation logic already exists and is exercised by the portal.
# Importing it keeps one implementation rather than a second copy that can drift.
sys.path.insert(0, str(REPO / "vidur_portal"))

import snippet_processor as vidur  # noqa: E402

app = FastAPI(title="South of Tethys — canon API", version="1.0.0")

# The game runs on Vite's dev port; a preview build on 4180. Both are local-only, which
# is the whole scope of this service today.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173", "http://127.0.0.1:4173",
        "http://localhost:4180", "http://127.0.0.1:4180",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class Place(BaseModel):
    """Where the player is standing, in the game's own vocabulary."""

    seed: str
    x: int
    y: int
    biome: str
    creature: str | None = None
    flora: str | None = None
    landmark: str | None = None
    question: str | None = Field(default=None, description="Overrides the derived query.")
    k: int = 5


# The portal's model is `lordlebu/4000BCSaraswaty`, which is GPT-2 small: 124M parameters
# and no instruction tuning. It retrieves nothing wrong -- retrieval is a separate,
# working system -- but it cannot write to a brief. Given real canon about the Lothal
# Marsh-Lurker and told not to invent anything, it produced a man holding a snake.
#
# So the model is a setting, not a constant. Point CANON_LLM at any instruction-tuned
# text-generation model and /ask starts working; leave it unset and the endpoint reports
# honestly rather than returning nonsense as though it were canon.
CANON_LLM = os.environ.get("CANON_LLM", "").strip()

_llm = None


def load_llm():
    global _llm
    if _llm is None:
        if CANON_LLM:
            from transformers import pipeline as hf_pipeline

            _llm = hf_pipeline("text-generation", model=CANON_LLM)
        else:
            _llm = vidur.get_hf_pipeline()
    return _llm


def as_query(place: Place) -> str:
    """Turn a tile into something worth asking canon.

    Naming the species matters more than naming the biome: "wetland" retrieves the biome
    entity, while "Lothal Marsh-Lurker" retrieves the creature, its region and the
    settlement it is named for.
    """
    if place.question:
        return place.question
    parts = [p for p in (place.creature, place.flora, place.landmark) if p]
    parts.append(f"{place.biome} of Jambhudweepa")
    return ", ".join(parts)


def sources(hits: list[dict]) -> list[dict]:
    return [
        {
            "entity_id": h["meta"].get("entity_id"),
            "name": h["meta"].get("name") or h["meta"].get("title"),
            "type": h["meta"].get("entity_type"),
            "source": h["meta"].get("source"),
            "distance": round(h.get("distance", 0.0), 4),
        }
        for h in hits
    ]


@app.get("/health")
def health() -> dict:
    """Enough for the game to decide whether to offer the feature at all."""
    count = None
    try:
        collection = vidur._get_collection()
        count = collection.count() if collection is not None else None
    except Exception:
        count = None
    return {
        "ok": True,
        "chroma": count is not None,
        "indexed_chunks": count,
        "collection": vidur.COLLECTION_NAME,
        "model": vidur.MODEL_HF,
        "persist_dir": os.environ.get("CHROMA_PERSIST_DIR", vidur.CHROMA_PERSIST_DIR),
    }


@app.post("/lore")
def lore(place: Place) -> dict:
    """What canon says about this tile. Retrieval only — no model, no waiting."""
    query = as_query(place)
    hits = vidur.retrieve(query, k=place.k)
    return {"query": query, "sources": sources(hits)}


@app.post("/ask")
def ask(place: Place) -> dict:
    """A written passage about this tile, grounded in the canon that was retrieved."""
    query = as_query(place)
    hits = vidur.retrieve(query, k=place.k)
    context = "\n\n".join(h["text"] for h in hits)

    instruction = (
        "You are the chronicler of Jambhudweepa, writing a traveller's journal in the "
        "second person. Using only the canon below, write two or three quiet sentences "
        "about what the traveller notices here. Do not invent creatures or places that "
        "are not named in the canon."
    )
    prompt = f"{instruction}\n\nCanon:\n{context}\n\nPlace: {query}\n\nJournal:"

    try:
        pipeline = load_llm()
        raw = pipeline(prompt, max_new_tokens=160)[0]["generated_text"]
    except Exception as exc:  # the model is the fragile part; the sources are not
        return {"query": query, "passage": None, "error": str(exc)[:200], "sources": sources(hits)}

    # HF text-generation returns the prompt followed by the continuation. Returning the
    # whole thing would print the instruction and the entire canon context to the player.
    passage = raw[len(prompt):].strip() if raw.startswith(prompt) else raw.strip()
    return {"query": query, "passage": passage or None, "sources": sources(hits)}
