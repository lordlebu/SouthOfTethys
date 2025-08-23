from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Use your Hugging Face model
MODEL = "lordlebu/4000BCSaraswaty"

@lru_cache(maxsize=1)
def get_hf_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


def prompt_llm(snippet: str, instruction: str) -> str:
    prompt = f"{instruction.strip()}\n\nSnippet: {snippet.strip()}"
    hf_pipeline = get_hf_pipeline()
    response = hf_pipeline(prompt, max_new_tokens=512)
    return response[0]["generated_text"]
