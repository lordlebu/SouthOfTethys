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
CANON_LLM=Qwen/Qwen2.5-7B-Instruct
```

Not every model on the Hub is served by an inference provider, and the error when one is not
is a flat "not supported by any provider". Two that worked on a free fine-grained token:

| model | passage time |
|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | 1.7-3.4s |
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

## Deploying

GitHub Pages is static and cannot run this, so the game and the service live apart: the walk
stays on Pages, the service goes somewhere that runs Python, and they meet over CORS.

### The part that matters more than hosting

This service holds your inference token. A public `/ask` therefore spends **your** money on
every call, and CORS is no defence -- it is a browser policy, and `curl` ignores it.

So the two endpoints are treated differently:

| | cost per call | online |
|---|---|---|
| `POST /lore` | none. Local retrieval against a local index. | public |
| `POST /ask` | real, at an inference provider | needs `X-Canon-Key` |

`CANON_API_KEY` sets that key. **It fails closed**: with hosted generation configured and no
key set, `/ask` returns 503 rather than serving an open, billable endpoint. Forgetting a
variable should cost a confusing error, not a bill. Without a key an `/ask` request 404s, so
a stranger learns nothing about what is there.

The game cannot hold that key -- anything the bundle ships is readable by everyone -- so a
public deployment offers retrieval only. `/health` reports `ask: open | key_required | locked`
and the panel hides the generate button when it may not use it. Generation stays available
locally, where the key is in your environment.

### Vercel — live

**https://south-of-tethys-canon.vercel.app**

| | |
|---|---|
| `GET /health` | public |
| `POST /lore` | public, ~2s |
| `POST /ask` | needs `X-Canon-Key`; 404 without it |

Deployed and verified: `/lore` returns the right entities for a tile, and `/ask` with the key
returns a Qwen-written passage grounded in them, in under four seconds.

### Vercel (how)

Vercel's Python runtime loads a top-level `app` from `app.py` and installs from
`requirements.txt`, so the FastAPI app runs unmodified. The free Hobby plan gives 2 GB of
memory, 1 vCPU and a **500 MB** Python bundle -- this bundle is 4.1 MB of code and index,
about 91 MB of dependencies, and an 86 MB model, so there is room to spare.

```bash
python services/api/build_deploy.py --target vercel   # -> dist-vercel/
cd dist-vercel
npx vercel deploy --prod
```

Set these on the Vercel project (Settings -> Environment Variables), never as `VITE_*`:

| name | value |
|---|---|
| `HF_TOKEN` | fine-grained token, Inference Providers only |
| `CANON_API_KEY` | a long random string |
| `CANON_LLM` | `Qwen/Qwen2.5-7B-Instruct` |
| `CANON_ALLOWED_ORIGINS` | `https://lordlebu.github.io` |

### Two things serverless broke, both found by deploying

The first deployment returned 200 on `/health` and **500 on every `/lore`**. Two separate
assumptions, each invisible locally:

**The index cannot be read in place.** Chroma opens its SQLite
read-write even to answer a query, and fails on a read-only mount with "attempt to write a
readonly database" -- which is exactly what a Vercel bundle is. `writable_index_dir()`
detects that and copies the 4 MB index to the one writable directory, once per cold start.
It probes the database file rather than the directory, because a directory can accept new
files while the files already in it are read-only, and it restores write permissions on the
copy, because `copytree` carries the read-only mode bits across and the copy would fail the
same way. In production `/health` now reports `persist_dir: /tmp/canon-chroma`, which is that
fallback working.

**The embedding model cannot be downloaded.** Chroma hardcodes its model cache to
`Path.home()/".cache"/"chroma"` with no setting to change it, and downloads 86 MB there on
first use. Serverless HOME is not writable, so the download failed and every retrieval 500d.
`_download_model_if_not_exists` skips the fetch when the extracted files are already present,
so the build ships them and `use_bundled_embedder()` repoints the class attribute. That also
removes the cold-start download entirely. The bundle goes from 4 MB to 91 MB and the built
function to 401 MB, still inside the 500 MB limit.

Neither of these can be caught by running the bundle locally, because a developer's
filesystem is writable and their cache is already warm. They only appear on a read-only
serverless mount.

### Hugging Face Spaces (needs PRO)

Docker Spaces are no longer free -- "hosting Gradio and Docker Spaces on free cpu-basic
requires a PRO subscription". Only Static Spaces are free, and they cannot run Python. The
Space target is kept for anyone who has PRO:

```bash
python services/api/build_deploy.py --target space
cd dist-space
git init && git add -A && git commit -m "Canon API"
git remote add space https://huggingface.co/spaces/<you>/<space>
git push space main --force
```

### Why not the others

| platform | verdict |
|---|---|
| **Koyeb** | Runs the container unmodified, but the free instance is 512 MB and **0.1 vCPU** -- a tenth of a core for ONNX inference -- and scales to zero after an hour. |
| **Cloudflare Workers** | Python Workers are Pyodide/PyEmscripten: no arbitrary C extensions, so `onnxruntime` and `chromadb` cannot run. A Cloudflare deployment means rewriting the service in TypeScript against Vectorize and Workers AI. Best architecture, real project. |
| **Supabase** | Edge Functions are Deno, so the service cannot live there; it would be the vector store only. Free projects **pause after a week of inactivity**, which is worse than a cold start for a demo. Worth revisiting when "the index needs a redeploy" starts to hurt -- that is the problem it solves. |

### Cold starts

A free Space sleeps when idle and takes tens of seconds to wake. The client probes twice for
exactly this reason -- a fast check so the common case of no service stays responsive, then a
longer one to give a waking host time to answer. Without the retry the first visitor of the
day would see no panel at all, and nothing would tell them why.
