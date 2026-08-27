
# South of Tethys - Procedural Storytelling Engine & Digital Book

A procedurally evolving storytelling engine inspired by world simulation games like **Dwarf Fortress** and **Caves of Qud**. This project manages story events, character genealogy, and evolving flora/fauna in a version-controlled Git repository. The digital book is generated automatically from these data and scripts.

## � Published Book & Artifacts

- **[View Published Book](https://lordlebu.github.io/SouthOfTethys/)** - The timeline and world data
- **[📖 Complete Timeline](index.md)** - Every event, by epoch and then by cause
- **[📊 Visual Timeline](timeline_mermaid.md)** - The epochs, and the causal graph of events
- **[⏰ Timeline Data](timeline.json)** - Raw event data in JSON format

## 🗺️ Maps

There is no published map, and the ones that used to be linked here have been removed rather
than left up. They described another project entirely — "Saltbluff Plateau", "Verdant Hollow",
a GeoJSON of Jambhudweepa and the Himalayas — none of which canon contains.

Canon states coordinates for its three field maps on an abstract 0–100 grid and nothing more,
so nothing correct can be generated in their place yet. See `docs/canon-integrity-plan.md` for
what modelling the geography actually requires.

## ✍️ Adding to canon

New story points go in `database/`, one JSON file per entity. **[database/AUTHORING.md](../database/AUTHORING.md)**
has copy-paste templates and the four steps. The one decision that matters is which folder:
nine reach the game's bundle and eight do not.

## 🚀 Publishing & Local Workflow

1. **Make changes** to timeline, characters, or world data
2. **Test locally**: `python utils/lint_story.py`
3. **Commit and push** to trigger automatic publication
4. **Manual publication**: Use GitHub Actions → "CI" → "Run workflow"

**Manual Code Quality Commands:**
Before running the following commands, make sure all tools are installed:
```bash
pip install -r requirements.txt
```

You can then run the following commands to auto-correct and lint your codebase (recommended: run on the `./utils` directory):

```bash
python -m black ./utils/*.py --line-length 88
python -m isort ./utils/*.py --profile black
python -m autoflake --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports ./utils/*.py
python -m pyupgrade --py39-plus ./utils/*.py
python -m flake8 ./utils/*.py
ruff check ./utils/*.py --fix
```

**Run Utility Scripts:**
- Lint and validate story data: `python utils/lint_story.py`
- Generate timeline summary and Mermaid diagram: `python utils/generate_timeline_mermaid.py`
- Generate the per-era atlas: `python utils/generate_atlas.py`
- Generate timeline (JSON): `python utils/generate_timeline.py`
- Simulate species evolution: `python utils/evolve_species.py`
- Process story snippets: see `vidur_portal/README.md`. The Ollama step this used to
  describe was replaced by the portal, and `utils/snippet_processor.py` no longer exists.

## 🎭 About This World

South of Tethys evolves procedurally through:
- **Collaborative storytelling** - Contributors add events, characters, and locations
- **Automated world-building** - Scripts track genealogy, species evolution, and consistency
- **Version-controlled narrative** - All changes tracked in Git for complete history
- **Dynamic publishing** - The book updates automatically with each world change

## 🔧 Technical Details

- **World Events**: Stored in JSON format with fantasy dates ("Act 1, Scene 2")
- **Characters**: Individual profiles with genealogy tracking
- **Species**: Flora and fauna with evolution chains
- **Geography**: GeoJSON format for mapping
- **Validation**: Automated consistency checking across all data

The source code and raw data are available in the [GitHub repository](https://github.com/lordlebu/SouthOfTethys).

---

*Last updated: {{DATE_PLACEHOLDER}}*

*Generated automatically from the South of Tethys world simulation engine*