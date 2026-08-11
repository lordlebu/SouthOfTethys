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

import json
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

# Hosted inference, when a token is available.
#
# Local generation turned out to have a ceiling rather than a tuning problem. GPT-2 small
# invents things; SmolLM2-360M either explains in the third person or, given examples,
# copies them back verbatim. The next size up would plausibly write, but ~1.5B on CPU is
# roughly sixteen seconds a passage, which is not a thing to put in a game about walking.
# So the model that can do this lives somewhere else.
#
# HF_TOKEN is read from the environment and never logged, never returned by /health, and
# never sent to the browser. The game talks to this service; this service talks to Hugging
# Face. A token that reached the client would be inlined into the public bundle.
HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

_llm = None
_client = None


def use_hosted() -> bool:
    return bool(HF_TOKEN and CANON_LLM)


def hosted_client():
    global _client
    if _client is None:
        from huggingface_hub import InferenceClient

        _client = InferenceClient(api_key=HF_TOKEN)
    return _client


def load_llm():
    """Local pipeline, for the no-token path. Kept, but it is not the recommended route."""
    global _llm
    if _llm is None:
        if CANON_LLM:
            from transformers import pipeline as hf_pipeline

            _llm = hf_pipeline("text-generation", model=CANON_LLM)
        else:
            _llm = vidur.get_hf_pipeline()
    return _llm


def redact(text: str) -> str:
    """Never let a token reach a response, a log or a browser, even inside an error."""
    if HF_TOKEN:
        text = text.replace(HF_TOKEN, "***")
    return text


_shots: str | None = None


def journal_examples(n: int = 3) -> str:
    """Real journal lines from canon, to show the voice rather than describe it.

    Read from the entities rather than hardcoded, so the examples cannot drift from what
    the game actually prints. The prototype starters are the oldest and most deliberately
    written of them, which makes them the best sample of the register.
    """
    global _shots
    if _shots is not None:
        return _shots

    lines: list[str] = []
    for f in sorted((REPO / "database" / "fauna").glob("*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        if payload.get("region") == "prototype-starters" and payload.get("journal_prompt"):
            lines.append(payload["journal_prompt"])
        if len(lines) >= n:
            break
    _shots = "\n".join(f"- {line}" for line in lines)
    return _shots


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

    # The journal's own sentences are the style guide. Describing the voice in prose made
    # small models write encyclopedia entries; showing them three real lines is shorter and
    # unambiguous. They come from canon, so the examples cannot drift from the game.
    shots = journal_examples()
    system = (
        "You are the chronicler of Jambhudweepa. Write one or two sentences for a traveller's "
        "journal: second person, present tense, plain and unhurried. Mention only what the canon "
        "names -- never invent a creature, plant or place. Do not explain or classify.\n\n"
        f"Examples of the voice:\n{shots}"
    )
    user = f"Canon:\n{context}\n\nPlace: {query}\n\nWrite the journal line."

    if use_hosted():
        try:
            completion = hosted_client().chat_completion(
                model=CANON_LLM,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                max_tokens=160,
                temperature=0.7,
            )
            passage = (completion.choices[0].message.content or "").strip()
            return {"query": query, "passage": passage or None, "sources": sources(hits)}
        except Exception as exc:
            # Never dress a failure up as canon: return the sources, say what went wrong.
            return {"query": query, "passage": None, "error": redact(str(exc))[:200],
                    "sources": sources(hits)}

    prompt = f"{system}\n\n{user}\n\nJournal:"
    try:
        pipeline = load_llm()
        raw = pipeline(prompt, max_new_tokens=160)[0]["generated_text"]
    except Exception as exc:
        return {"query": query, "passage": None, "error": redact(str(exc))[:200], "sources": sources(hits)}

    # HF text-generation returns the prompt followed by the continuation. Returning the
    # whole thing would print the instruction and the entire canon context to the player.
    passage = raw[len(prompt):].strip() if raw.startswith(prompt) else raw.strip()
    return {"query": query, "passage": passage or None, "sources": sources(hits)}
