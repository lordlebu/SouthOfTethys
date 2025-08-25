import os
from functools import lru_cache

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

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


def prompt_llm(snippet: str, instruction: str) -> str:
    prompt = f"{instruction.strip()}\n\nSnippet: {snippet.strip()}"
    hf_pipeline = get_hf_pipeline()
    response = hf_pipeline(prompt, max_new_tokens=512)
    return response[0]["generated_text"]
