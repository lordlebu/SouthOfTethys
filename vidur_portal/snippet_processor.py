from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Anchored to the repo root so `streamlit run` works from either the repo root
# or vidur_portal/, rather than resolving against the current working directory.
CHROMA_PERSIST_DIR = os.environ.get(
    "CHROMA_PERSIST_DIR", str(REPO_ROOT / "storage" / "chroma")
)
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = "southoftethys"

DEFAULT_INSTRUCTION = (
    "Extract the characters, events, and timeline entries from the snippet below. "
    "Follow SouthOfTethys conventions and return structured data."
)

# Optional Chroma imports (retrieval works with no HF model loaded)
CHROMA_ENABLED = False
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions

    CHROMA_ENABLED = True
except Exception:
    CHROMA_ENABLED = False

# Local model paths
LOCAL_CONFIG = os.path.join(
    os.path.dirname(__file__), "..", "..", "model", "config", "config.json"
)
LOCAL_CHECKPOINT = os.path.join(
    os.path.dirname(__file__), "..", "..", "model", "checkpoints", "pytorch_model.bin"
)
MODEL_HF = "lordlebu/4000BCSaraswaty"
FALLBACK_MODEL = "gpt2"  # Use a public model for fallback


@lru_cache(maxsize=1)
def get_hf_pipeline():
    # Imported lazily: loading transformers pulls torch and can trigger a model
    # download, and retrieval must stay usable without either.
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    try:
        if os.path.exists(LOCAL_CONFIG) and os.path.exists(LOCAL_CHECKPOINT):
            tokenizer = AutoTokenizer.from_pretrained(os.path.dirname(LOCAL_CONFIG))
            model = AutoModelForCausalLM.from_pretrained(
                os.path.dirname(LOCAL_CHECKPOINT)
            )
        else:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_HF)
            model = AutoModelForCausalLM.from_pretrained(MODEL_HF)
        return pipeline("text-generation", model=model, tokenizer=tokenizer)
    except Exception as e:
        print(
            f"Model loading failed: {e}\nFalling back to public model '{FALLBACK_MODEL}'."
        )
        tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL)
        model = AutoModelForCausalLM.from_pretrained(FALLBACK_MODEL)
        return pipeline("text-generation", model=model, tokenizer=tokenizer)


@lru_cache(maxsize=1)
def _get_collection():
    """Return the canon collection, or None when no index has been built yet."""
    if not CHROMA_ENABLED:
        return None
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    if cloud_key:
        client = chromadb.CloudClient(
            api_key=cloud_key,
            tenant=os.environ.get("CHROMA_TENANT"),
            database=os.environ.get("CHROMA_DATABASE"),
        )
    else:
        client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
    # Same embedding function the indexer used, so queries land in that vector space.
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    try:
        return client.get_collection(COLLECTION_NAME, embedding_function=ef)
    except Exception:
        return None


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Top-k canon chunks for a query, each with its source metadata.

    Returns [] when Chroma is unavailable or the collection has not been indexed.
    """
    collection = _get_collection()
    if collection is None or not query.strip():
        return []

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["metadatas", "documents", "distances"],
    )
    # Chroma nests one list per query; we only ever send one.
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    return [
        {"text": doc, "meta": meta or {}, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


def prompt_llm(
    snippet: str,
    instruction: str = DEFAULT_INSTRUCTION,
    use_retrieval: bool = True,
) -> str:
    prompt_prefix = instruction.strip()
    retrieved = []
    if use_retrieval and CHROMA_ENABLED:
        retrieved = retrieve(snippet, k=5)
    # build context
    context = "\n\n".join([r.get("text", "") for r in retrieved])
    if context:
        prompt = f"{prompt_prefix}\n\nContext:\n{context}\n\nSnippet: {snippet.strip()}"
    else:
        prompt = f"{prompt_prefix}\n\nSnippet: {snippet.strip()}"

    hf_pipeline = get_hf_pipeline()
    response = hf_pipeline(prompt, max_new_tokens=512)
    return response[0]["generated_text"]
