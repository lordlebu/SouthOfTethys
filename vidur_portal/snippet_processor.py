import os
from functools import lru_cache
from typing import Optional, List, Dict

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Optional Chroma imports (lazy)
CHROMA_ENABLED = False
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "../storage/chroma")
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer

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


def _retrieve_with_chroma(query: str, k: int = 5) -> List[Dict]:
    """Return a list of metadata + text for top-k hits from Chroma."""
    if not CHROMA_ENABLED:
        return []
    cloud_key = os.environ.get("CHROMA_CLOUD_API_KEY")
    collection = None
    if cloud_key:
        tenant = os.environ.get("CHROMA_TENANT")
        database = os.environ.get("CHROMA_DATABASE")
        client = chromadb.CloudClient(api_key=cloud_key, tenant=tenant, database=database)
        try:
            collection = client.get_collection("southoftethys")
        except Exception:
            return []
    else:
        client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_PERSIST_DIR))
        try:
            collection = client.get_collection("southoftethys")
        except Exception:
            return []

    # Use a small embedding model for retrieval
    embedder = SentenceTransformer(
        os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )
    q_emb = embedder.encode([query])[0]
    results = collection.query(
        vector=q_emb, n_results=k, include=["metadatas", "documents"]
    )
    hits = []
    for doc, meta in zip(results.get("documents", []), results.get("metadatas", [])):
        hits.append({"text": doc, "meta": meta})
    return hits


def prompt_llm(
    snippet: str, instruction: str, use_retrieval: Optional[bool] = True
) -> str:
    prompt_prefix = instruction.strip()
    retrieved = []
    if use_retrieval and CHROMA_ENABLED:
        retrieved = _retrieve_with_chroma(snippet, k=5)
    # build context
    context = "\n\n".join([r.get("text", "") for r in retrieved])
    if context:
        prompt = f"{prompt_prefix}\n\nContext:\n{context}\n\nSnippet: {snippet.strip()}"
    else:
        prompt = f"{prompt_prefix}\n\nSnippet: {snippet.strip()}"

    hf_pipeline = get_hf_pipeline()
    response = hf_pipeline(prompt, max_new_tokens=512)
    return response[0]["generated_text"]
