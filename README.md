# South of Tethys

The **canon** for a shared fictional world, and the tools that keep it honest.

Everything canonical lives in [`database/`](database/) as one JSON file per entity, validated
against JSON Schema and checked on every push — currently **v1.6.0, 504 entities**:

| | |
|---|---|
| **Species** | 256 fauna, 90 flora |
| **World** | 7 regions, 2 settlements, 41 characters, 12 events, 3 factions, 3 artifacts |
| **Field diary** | 4 field maps, 24 points of interest, 31 discoveries, 8 field questions, 10 people, 10 words |

## Two repositories, one world

This one owns **what exists and what is true**. Its sibling,
[4000BCESaraswathy](https://github.com/lordlebu/4000BCESaraswathy), is a browser game —
*Varuna's Field Diary* — that owns **what a particular player did and how it looks**.

The split holds because everything canon holds is a *noun* — places, species, discoveries,
people, words — and everything the game holds is a *verb* or a *view*. Canon exports its own
shape and the game owns adapters that translate it, so a change to the game's types never
reaches back into a schema here.

```
database/  →  utils/export_canon_bundle.py  →  the game's data/canon/  →  src/content/*.ts
```

That bundle is generated and must never be hand-edited; a lock file and the game's CI enforce it.

## Start here

```bash
pip install -r requirements.txt

python utils/lint_story.py          # schemas, index counts, every cross-reference resolves
python utils/check_playability.py   # can a player actually reach everything authored
```

Both gate every push. `check_playability.py` is a simulation rather than a set check — it starts
from nothing and repeatedly does whatever has become possible, because asking instead whether
each requirement is "obtainable somewhere" passes a dependency cycle, and one shipped.

To publish changes to the game and the live service:

```bash
python utils/export_canon_bundle.py --apply    # write the game's bundle
```

Merging to `main` rebuilds and redeploys the retrieval service by itself, then checks the live
index actually covers canon.

## What is published

- **[The book](https://lordlebu.github.io/SouthOfTethys/)** — timeline, maps and world data
- **[Interactive world map](https://lordlebu.github.io/SouthOfTethys/interactive_map.html)**
- **[Visual timeline](https://lordlebu.github.io/SouthOfTethys/timeline_mermaid.html)**
- **[The game](https://lordlebu.github.io/4000BCESaraswathy/)** — the walk, built from this canon
- **Retrieval API** — `/lore` for a place, `/search` for a question, `/ask` for a written passage

Publishing is automatic on push. See [docs/PUBLISHING.md](docs/PUBLISHING.md) for the manual route.

## Where the reasoning is written down

| File | What it holds |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | orientation for agents working here |
| [`docs/decisions.md`](docs/decisions.md) | every call made on the project's behalf, and what is still open |
| [`DESIGN.md`](DESIGN.md) | the binding rulings: the era, authored anchors, build-time reading |
| [`database/TODO.md`](database/TODO.md) | which entities are missing |

Read `docs/decisions.md` before changing anything structural.

---

## Developer checklist: Chroma index

1. Install dependencies:
```bash
pip install -r services/chroma/requirements.txt
```
2. Build the index locally from `database/`:
```bash
REPO_DIR=$(pwd) CHROMA_PERSIST_DIR=storage/chroma python services/chroma/index_chroma_service.py
```
3. Check retrieval without starting the portal:
```bash
CHROMA_PERSIST_DIR=storage/chroma python scripts/query_chroma.py "Who is Kavik Stoneheart?"
```
4. Update the index after editing a single entity:
```bash
python scripts/index_changes.py --files database/characters/character_kavik.json
```
5. Configure the portal (optional env vars): `CHROMA_PERSIST_DIR`, `EMBEDDING_MODEL`.
6. Add `storage/chroma/` to `.gitignore` (already added).

CI: Run only smoke tests that verify the portal can read a persisted index; do not build or store vectors in CI.

## Schema validation (Chroma)

We validate vector metadata payloads against JSON Schemas before inserting into Chroma. A set of example fixtures lives under `services/chroma/schemas/fixtures/` and can be validated locally.

Manual validation command (PowerShell / Bash):
```powershell
python services/chroma/schemas/validate_metadata.py events services/chroma/schemas/fixtures/event_fixture.json
python services/chroma/schemas/validate_metadata.py characters services/chroma/schemas/fixtures/character_fixture.json
python services/chroma/schemas/validate_metadata.py snippets services/chroma/schemas/fixtures/snippet_fixture.json
python services/chroma/schemas/validate_metadata.py documents services/chroma/schemas/fixtures/document_fixture.json
```

Pre-commit hook:
- The repository includes a local `.git/hooks/pre-commit` script that runs code formatters, linters, and the Chroma schema validation checks against the fixtures.
- The hook will fail commits if any fixture validation fails. The Hugging Face push test in the hook runs only when `HF_TOKEN` is set in your environment (do not store the token in git).

To enable the local Git hook (if not already present):
```bash
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```


## Docker local stack (Vidur Portal + Chroma indexer)

You can build and run a local Docker stack that populates a persistent Chroma index and runs the Vidur Portal.

Build and run the portal and indexer:
```powershell
docker compose -f docker-compose.chroma.yml up --build
```

This will:
- Build the `vidur` service (Streamlit app).
- Run the `indexer` one-shot service which creates the Chroma index in the `chroma_data` volume.
- Expose Streamlit on http://localhost:8501

To rebuild the index, re-run the indexer service only:
```powershell
docker compose -f docker-compose.chroma.yml run --rm indexer
```

---

## 🛡️ Pre-commit Integration Steps

1. **Place your `.pre-commit-config.yaml` in the project root.**
2. **Add tool-specific configs** (`.flake8`, `pyproject.toml`, `mypy.ini`, `.bandit.yml`) as described in the repo or documentation.
3. **Run `pre-commit install`** to activate hooks for all contributors:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. **Run manually (optional):**
   ```bash
   pre-commit run --all-files
   ```

#### Local Auto-formatting with `.git/hooks/pre-commit`

For additional local enforcement, you can use a custom pre-commit hook script in `.git/hooks/pre-commit` to automatically run code formatters and linters before each commit.  
This script will run tools like `black`, `isort`, `autoflake`, `pyupgrade`, `ruff`, and `flake8` on all Python files in the project.

**Sample usage:**
```bash
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
This ensures code quality and formatting are enforced locally before changes are committed.  
**Note:** The CI pipeline only runs lint checks and does not auto-fix or format code.

### Manual Code Quality Commands

Before running the following commands, make sure all tools are installed:
```bash
pip install -r requirements.txt
```

You can then run the following commands to auto-correct and lint your codebase (recommended: run on the entire project):

```bash
python -m black ./**/*.py --line-length 88
python -m isort ./**/*.py --profile black
python -m autoflake --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports ./**/*.py
python -m pyupgrade --py39-plus ./**/*.py
python -m flake8 ./**/*.py
python -m ruff check ./**/*.py --fix
```

### Recommended Minimal Setup
For most Python projects, start with:

- `black` (formatting)
- `isort` (imports)
- `flake8` (linting)
- `pre-commit-hooks` (basic hygiene)

Add `mypy`, `bandit`, and others as your codebase grows or if you need stricter checks.

---

## Story snippets

Snippets are processed through the [Vidur Portal](vidur_portal/README.md), a separate web app,
which replaced an earlier Ollama workflow.

**A correction worth making plainly:** this README used to describe "our own Hugging Face AI
model". The weights at [lordlebu/4000BCSaraswaty](https://huggingface.co/lordlebu/4000BCSaraswaty)
are **stock GPT-2, unmodified, and nothing in the project uses them** — a 124M base model with no
instruction tuning cannot write to a brief, which is why the service moved to retrieval plus an
instruction-tuned model chosen at runtime by `CANON_LLM`. See [`model/README.md`](model/README.md).

Model pushes are performed locally with `utils/test_hf_push.py`; CI does not push models.

---

## Where this is going

A living worldbuilding engine rather than a finished world — one where structure and prose
reinforce each other instead of drifting apart:

- Canon that a machine can validate and a person can read, in the same files
- Dynamic timelines, genealogies and species evolution, all cross-referenced
- Tools that let writers and developers build, validate and visualise the same world
- Everything explorable and reusable through open formats and a public retrieval API
- A game that is *made of* the canon rather than a copy of it

## Chronology of Jambudweepa  
*From Primordial Seas to City-States*  

---

### ⏳ **Prehistoric Foundations**  
#### (c. 500–250 Million Years Ago)  
- **Invertebrate Dominion**:  
  Ammonoids rule shallow seas. The **Ammonite Man** emerges as first spiritual entity - a cephalopod sage whispering through coral reefs.  
- **Avian-Synapsid Epoch**:  
  Flightless therapod birds and sail-backed synapsids dominate landmasses. **Owlman** appears as nocturnal guardian of forests.  

---

### 🐒 **Age of Vanaras**  
#### (c. 50–5 Million Years Ago)  
1. **Vanara Zenith**:  
   - Proto-primates develop tool use and fire mastery in **Gondwana forests**  
   - Build tree-cities in the **Nilgiri Canopy** (southern Jambudweepa)  
2. **Great Devolvement**:  
   - Climate shifts fracture civilization  
   - Descendants regress to modern monkeys  
   - **Lionman** appears as sun-spirit guiding scattered tribes  

---

### 🚶 **Human Migrations**  
*(Wave Settlement Pattern: Northwest → East/South)*  

| **Era**         | **Group**       | **Origin**          | **Settlement**          | **Key Traits**                  |  
|-----------------|-----------------|---------------------|-------------------------|---------------------------------|  
| c. 50,000 BCE | **Jharwa**      | Zagros Mountains    | Saraswati Delta         | Cave painters, shell worshippers |  
| c. 10,000 BCE | **Vedda**       | Caspian Steppes     | Ganges Plain            | Horse tamers, fire ritualists    |  
| c. 5,000 BCE  | **Naga**        | Indus Valley        | Deccan Plateau          | Serpent cults, metalworkers      |  
| c. 3,000 BCE  | **Outliers**    | Hybrid populations  | Fringe regions          | Vanara-human mixes, bird-speakers |  

---

### 🌀 **Spiritual Beings & Gates**  
#### (Timeless Entities)  
| **Being**         | **Manifestation**                     | **Domain**               |  
|-------------------|---------------------------------------|--------------------------|  
| **Ammonite Man**  | Spiraling nautilus-shell form         | Tethys Sea depths        |  
| **Owlman**        | Feathered humanoid with 360° neck     | Deciduous forests        |  
| **Lionman**       | Maned solar deity with obsidian claws | Deserts/Savannas         |  
| **Gatekeepers**   | Shape-shifting stone sentinels        | Dwarka portals           |  

### 🔮 **Interdimensional Gates**  
- **Dwarka Mechanism**:  
  Stone arches pulsating with blue energy, appearing at cosmic alignments  
  - **Function**: Bridges physical realm with **Asura Loka** (demon dimension)  
  - **Current Status**: Dormant beneath Dwarka city's foundations  
- **Other Portals**:  
  - **Yaksha Gates**: Hidden in Narmada Valley monoliths  
  - **Rakshasha Vortices**: Swirling sand pits in Gedrosian Desert  

---

### 🏺 **Civilization Dawn**  
#### (c. 3000–500 BCE)  
1. **Harappan Emergence** (NW Origin):  
   - Cities rise along Saraswati River (Lothal, Dholavira)  
   - Trade with **Naga serpent-kingdoms** in Deccan  
2. **Eastern Expansion**:  
   - Vedda clans migrate to Ganges Delta  
   - Found **Magadha** kingdom with Yaksha aid  
3. **Southern Hybrids**:  
   - Jharwa-Vanara tribes build **tree-temples** in Western Ghats  
   - Worship Owlman as night guardian  

---

### 👁️‍🗨️ **Current Era** (c. 500 BCE–Present)  
| **Realm**         | **Inhabitants**                       | **Status**               |  
|-------------------|---------------------------------------|--------------------------|  
| **City-States**   | Humans (Vedda/Naga dominant)          | Flourishing              |  
| **Forest Fringes**| Vanara remnants, hybrid tribes        | Declining                |  
| **Mountain Holds**| Yaksha stone-smiths                   | Isolationist             |  
| **Desert Wastes** | Rakshasha nomad clans                 | Increasingly visible     |  

> *"The gates remember what mortals forget. When stars align, shadows walk."*  
> ― Yaksha inscription, Narmada monolith  

---

**Chronological Anchors**  
- 🌋 **KT Extinction**: Allowed avian-therapod dominance  
- ❄️ **Pleistocene Glaciation**: Triggered Vanara collapse  
- ⛵ **Saraswati Drying**: Forced human eastward migration  

**Unresolved Mysteries**  
- Where did Owlman retreat during the Vedda conquest?  
- Why do Dwarka gates activate during solar eclipses?  
- Are Ammonite Man and Lionman opposing forces?  

---  
**🕰️ Timeline Key**  
- **Bold** = Evolutionary turning points  
- *Italics* = Spiritual manifestations
