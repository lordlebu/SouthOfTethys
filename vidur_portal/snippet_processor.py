import json
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Use your Hugging Face model
MODEL = "lordlebu/4000BCSaraswaty"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL)
hf_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

def prompt_llm(snippet: str, instruction: str) -> str:
    prompt = f"{instruction.strip()}\n\nSnippet: {snippet.strip()}"
    response = hf_pipeline(prompt, max_new_tokens=512)
    return response[0]["generated_text"]
