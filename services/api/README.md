# Canon API

The HTTP seam between the canon database and the game. Optional: the game is a static
bundle with canon baked in, and it works exactly as before when nothing is listening.

## Run the demo

Three terminals. The order matters only in that the index must exist before the service
can answer.

```bash
# 1. index canon — needed once, and again after any canon change
cd SouthOfTethys
REPO_DIR=. CHROMA_PERSIST_DIR=storage/chroma python services/chroma/index_chroma_service.py

# 2. the service
pip install -r services/api/requirements.txt
CHROMA_PERSIST_DIR=storage/chroma uvicorn services.api.main:app --port 8000

# 3. the game — point it at the service, which is off by default
cd ../4000BCESaraswathy
cp .env.example .env.local     # then uncomment VITE_CANON_API
npm run dev                    # http://localhost:4173/?seed=lothal
```

Walk a few tiles. An **Ask the canon** panel appears in the sidebar; it retrieves the canon
entities for the tile you are standing on.

`VITE_CANON_API` is what switches this on, and it is deliberately unset by default: without
it the game makes no network calls at all and the panel never renders. That is not only the
shipping default but the one CI runs — an earlier version defaulted to `localhost:8000` and
probed on every page load, and the refused request wrote a console error that failed two
browser specs.

## Endpoints

| | |
|---|---|
| `GET /health` | whether Chroma is reachable and how many chunks are indexed |
| `POST /lore` | retrieval only. ~100ms warm. The reliable half. |
| `POST /ask` | retrieval plus a generated passage. Seconds, and see the warning below. |

Both POST endpoints take a tile: `{seed, x, y, biome, creature?, flora?, landmark?, k?}`.

```bash
curl -s -X POST localhost:8000/lore -H 'Content-Type: application/json' \
  -d '{"seed":"lothal","x":12,"y":7,"biome":"wetland","creature":"Lothal Marsh-Lurker"}'
```

## The model cannot write yet

`lordlebu/4000BCSaraswaty` is GPT-2 small — 124M parameters, no instruction tuning. It
loads and runs, and it is useless for this. Given real canon about the Lothal Marsh-Lurker
and told explicitly not to invent anything, it produced a man holding a snake, and with a
longer prompt it produced a repeating book citation.

This is a capability ceiling, not a prompt or context problem: a canon chunk is ~119 tokens
against a 1024-token window, so there is plenty of room.

So the model is a setting. Point `CANON_LLM` at any instruction-tuned text-generation model
and `/ask` starts working:

```bash
CANON_LLM=Qwen/Qwen2.5-0.5B-Instruct CHROMA_PERSIST_DIR=storage/chroma \
  uvicorn services.api.main:app --port 8000
```

`/lore` is unaffected and is what the demo currently rests on — retrieval is a separate,
working system that returns the right entity at a distance of ~0.29.

## Scope

Local only. CORS allows `localhost:4173` and `:4180` and nothing else, and there is no
auth, no rate limiting and no caching beyond what the browser client does per tile.
Deploying this means a host that runs Python — GitHub Pages cannot — plus swapping local
`transformers` for a hosted inference endpoint.

## Generation, and why it needs a hosted model

Retrieval works well. Generation was the hard part, and the finding is that it is a model
problem rather than a prompting one:

| model | speed (CPU, ~90 tokens) | result |
|---|---|---|
| `lordlebu/4000BCSaraswaty` (GPT-2 small, 124M) | ~2s | invents things the canon never named |
| `SmolLM2-360M-Instruct` | 4s measured | grounded, but writes encyclopedia entries; given examples it copies them back verbatim |
| ~1.5B | ~16s extrapolated | plausibly writes, but too slow for a game about walking |

Small enough to feel responsive is too small to write; large enough to write is too slow
locally. So `/ask` uses hosted inference when it can.

```bash
# in SouthOfTethys/.env.local  — gitignored, never committed
HF_TOKEN=hf_...
CANON_LLM=meta-llama/Llama-3.1-8B-Instruct
```

Not every model on the Hub is served by an inference provider, and the error when one is not
is a flat "not supported by any provider". Two that worked on a free fine-grained token:

| model | passage time |
|---|---|
| `meta-llama/Llama-3.1-8B-Instruct` | 1.7-3.4s |
| `Qwen/Qwen2.5-7B-Instruct` | similar |

`Llama-3.2-3B-Instruct`, `Mistral-7B-Instruct-v0.3`, `zephyr-7b-beta`, `Phi-3.5-mini-instruct`
and `gemma-2-2b-it` were all refused. Probe before assuming.

`.env.local` is read automatically -- python-dotenv is a dependency for exactly that, because
the README used to point at a file nothing loaded.

Then start the service with those in the environment. `use_hosted()` is true only when both
are set; with neither, `/ask` falls back to the local pipeline, and with a token but no model
it stays local too.

**The token never leaves this service.** It is not returned by `/health`, and `redact()`
strips it from any error before it reaches a response. Never put it in a `VITE_` variable:
Vite inlines those into the game's public bundle.

The style examples in the prompt are read from canon (`utils/export_game_data.py` writes the
same sentences into the game), so the voice shown to the model cannot drift from the voice
the player reads.
