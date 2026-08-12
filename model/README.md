---
language: en
license: mit
library_name: transformers
pipeline_tag: text-generation
tags:
  - text-generation
  - SouthOfTethys
  - not-fine-tuned
---

# 4000BCSaraswaty

**This is stock GPT-2 small (124M), unmodified. It is not a fine-tuned model, and nothing in
the South of Tethys project uses it.** It is published here for provenance, and this card
exists so that nobody mistakes it for the thing its name suggests.

## What it actually is

An early experiment from the project's first weeks. The intent was to fine-tune a small model
on the South of Tethys canon; what was published was the base checkpoint, before any training
happened. The export script still says so in a comment:

```python
model_name = "gpt2"  # Replace with your fine-tuned model if you have one
```

No replacement ever happened, and it should not now — see below.

## Why it was never updated

Because the approach was abandoned, and for a good reason rather than through neglect.

GPT-2 small has no instruction tuning. Given real canon about the Lothal Marsh-Lurker and told
plainly not to invent anything, it produced a description of a man holding a snake. Retrieval
was never the problem — that part works and is a separate system — but a 124M base model cannot
write to a brief, and no amount of prompting fixes that.

The project moved to retrieval-augmented generation against an instruction-tuned model, chosen
at runtime. The live service points at `Qwen/Qwen2.5-7B-Instruct` and never loads this
checkpoint.

## What to use instead

The canon itself, which is the part with any value in it:

- **Entities** — around 470 authored records: species, regions, places, discoveries, people
  and vocabulary, in [`database/`](https://github.com/lordlebu/SouthOfTethys) with JSON Schema
  and a lint that enforces referential integrity.
- **Retrieval** — a Chroma index over the whole corpus, served behind a small FastAPI service.
  `/lore` answers "what does canon say about this place" from the entities themselves.
- **Generation** — any instruction-tuned model, set by environment variable. The service holds
  no opinion about which, and swapping it is a config change.

## Should you build on this?

No. It is `gpt2`, and you should use `gpt2` — you will get an identical model with a clearer
name and a proper card. This repository is kept because deleting published artifacts breaks
links and hides history, not because it is useful.
