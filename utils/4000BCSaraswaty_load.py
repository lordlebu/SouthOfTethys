from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "lordlebu/4000BCSaraswaty"  # or local path to your model folder

# Try loading the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Test a simple generation
inputs = tokenizer("Hello world!", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0]))