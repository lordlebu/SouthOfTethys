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
from hmac import compare_digest
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

REPO = Path(__file__).resolve().parents[2]

# The README told people to put HF_TOKEN in .env.local, and nothing read it -- the service
# looked at os.environ only, so a correctly filled file would have been silently ignored and
# /ask would have quietly stayed on the local model. Load it here, without overriding
# anything already exported in the shell.
try:
    from dotenv import load_dotenv

    load_dotenv(REPO / ".env.local", override=False)
    load_dotenv(REPO / ".env", override=False)
except ImportError:  # optional; exporting the vars by hand still works
    pass

def writable_index_dir() -> str:
    """Where Chroma should read the index from, given the filesystem it has.

    Chroma opens its SQLite read-write even to answer a query, and fails outright on a
    read-only mount with "attempt to write a readonly database". Serverless platforms ship
    the bundle read-only and give you one writable directory, so on those the index has to be
    copied somewhere writable before it can be opened at all.

    The copy is ~4MB and happens once per cold start. It is skipped entirely when the
    directory is already writable, which is every local run.
    """
    configured = os.environ.get("CHROMA_PERSIST_DIR") or str(REPO / "storage" / "chroma")
    src = Path(configured)
    if not src.exists():
        return configured

    # Probe the database file itself, not the directory. Chroma needs to write to the
    # existing sqlite even for a read, and a directory can accept new files while the files
    # already in it are read-only -- so a touch-and-delete probe reports writable and the
    # first query still fails.
    db = src / "chroma.sqlite3"
    try:
        if db.exists():
            with open(db, "r+b"):
                pass
        else:
            probe = src / ".write-probe"
            probe.touch()
            probe.unlink()
        return configured
    except OSError:
        pass

    import shutil
    import stat
    import tempfile

    dst = Path(tempfile.gettempdir()) / "canon-chroma"
    if not dst.exists():
        shutil.copytree(src, dst)
        # copytree carries the mode bits across, so a copy of a read-only bundle is itself
        # read-only and Chroma fails exactly as it would have in place. Restore write.
        for path in dst.rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
    return str(dst)


# Must happen before snippet_processor is imported: it reads CHROMA_PERSIST_DIR into a
# module-level constant, so setting it afterwards would have no effect.
os.environ["CHROMA_PERSIST_DIR"] = writable_index_dir()


def use_bundled_embedder() -> None:
    """Point Chroma's ONNX embedder at a model shipped with the bundle.

    Chroma hardcodes its model cache to `Path.home()/".cache"/"chroma"`, downloads 86MB
    there on first use, and has no setting for it. On a serverless platform HOME is not
    writable, so the download fails and every retrieval 500s -- which is exactly what the
    first deployment did.

    `_download_model_if_not_exists` skips the fetch entirely when the six extracted files
    are already present, so shipping them and repointing the class attribute means no
    download, no writable HOME, and no cold-start fetch. Absent, this does nothing and the
    normal download path applies -- which is what happens on a developer's machine.
    """
    bundled = REPO / "models" / "onnx_models" / "all-MiniLM-L6-v2"
    if not (bundled / "onnx" / "model.onnx").exists():
        return
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

    ONNXMiniLM_L6_V2.DOWNLOAD_PATH = bundled


use_bundled_embedder()

# The retrieval and generation logic already exists and is exercised by the portal.
# Importing it keeps one implementation rather than a second copy that can drift.
sys.path.insert(0, str(REPO / "vidur_portal"))

import snippet_processor as vidur  # noqa: E402

app = FastAPI(title="South of Tethys — canon API", version="1.1.0")

# Vite's dev port and a preview build on 4180. A deployment adds its own origin --
# CANON_ALLOWED_ORIGINS is comma-separated, e.g. "https://lordlebu.github.io".
LOCAL_ORIGINS = [
    "http://localhost:4173", "http://127.0.0.1:4173",
    "http://localhost:4180", "http://127.0.0.1:4180",
]
ALLOWED_ORIGINS = LOCAL_ORIGINS + [
    o.strip() for o in os.environ.get("CANON_ALLOWED_ORIGINS", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*", "X-Canon-Key"],
)

# /lore is free to serve: local retrieval against a local index, no external call, no
# per-request cost. /ask spends real money at an inference provider on every call, and CORS
# is no defence -- it is a browser policy, and curl ignores it entirely. So /ask takes a key.
#
# It fails closed on purpose. If hosted generation is switched on and no key is configured,
# /ask refuses rather than serving an open endpoint that bills the owner: forgetting to set
# a variable should cost a confusing error, not a bill.
CANON_API_KEY = os.environ.get("CANON_API_KEY", "").strip()


def ask_access() -> str:
    """`open` locally, `key_required` when a key is set, `locked` when one is needed and absent."""
    if CANON_API_KEY:
        return "key_required"
    if use_hosted():
        return "locked"
    return "open"


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
        # The model actually used for /ask, which is not the portal's once CANON_LLM is set.
        # Reporting vidur.MODEL_HF here said GPT-2 while Llama was doing the writing.
        "model": CANON_LLM or vidur.MODEL_HF,
        "generation": "hosted" if use_hosted() else "local",
        # The game reads this to decide whether to offer "Write a passage" at all.
        "ask": ask_access(),
        "persist_dir": os.environ.get("CHROMA_PERSIST_DIR", vidur.CHROMA_PERSIST_DIR),
    }


@app.post("/lore")
def lore(place: Place) -> dict:
    """What canon says about this tile. Retrieval only — no model, no waiting."""
    query = as_query(place)
    hits = vidur.retrieve(query, k=place.k)
    return {"query": query, "sources": sources(hits)}


class Question(BaseModel):
    """A question in the player's own words, rather than a tile."""

    query: str
    k: int = 5


@app.post("/search")
def search(question: Question) -> dict:
    """
    Retrieval over the whole corpus, for a question nobody wrote a tile for.

    `/lore` answers "what does canon say about where I am standing", which is the shape the
    game needed first and is useless for "has anything like this been seen before". This takes
    words instead of coordinates.

    Public and retrieval-only, exactly like `/lore`: it runs no model, spends nothing, and
    returns which canon entities are nearest rather than prose about them. Generation stays
    behind `/ask` and its key.
    """
    query = (question.query or "").strip()
    if not query:
        return {"query": "", "sources": []}
    # Bounded rather than trusted: k comes from a client and a large one is a cheap way to
    # make the service do real work on somebody else's behalf.
    hits = vidur.retrieve(query, k=max(1, min(question.k, 20)))
    return {"query": query, "sources": sources(hits)}


@app.post("/ask")
def ask(place: Place, x_canon_key: str | None = Header(default=None)) -> dict:
    """A written passage about this tile, grounded in the canon that was retrieved."""
    access = ask_access()
    if access == "locked":
        raise HTTPException(
            status_code=503,
            detail=("Generation is configured but unprotected, so it is disabled. Set "
                    "CANON_API_KEY, or unset HF_TOKEN/CANON_LLM to fall back to local generation."),
        )
    if access == "key_required" and not compare_digest(x_canon_key or "", CANON_API_KEY):
        # 404 rather than 401: an unauthenticated caller learns nothing about what is here.
        raise HTTPException(status_code=404, detail="Not found.")

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
