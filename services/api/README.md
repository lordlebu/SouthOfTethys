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
