
# South of Tethys - Procedural Storytelling Engine & Digital Book

A procedurally evolving storytelling engine inspired by world simulation games like **Dwarf Fortress** and **Caves of Qud**. This project manages story events, character genealogy, and evolving flora/fauna in a version-controlled Git repository. The digital book is generated automatically from these data and scripts.

## � Published Book & Artifacts

- **[View Published Book](https://lordlebu.github.io/SouthOfTethys/)** - Complete timeline, maps, and world data
- **[📖 Complete Timeline](index.md)** - Full chronological story from prehistoric times to present
- **[📊 Visual Timeline](timeline_mermaid.md)** - Interactive flowchart of major events
- **[🗺️ Interactive World Map](interactive_map.html)** - Explore the world geography

## 🌍 World Data

- **[📍 Geographic Data](regions.geojson)** - Detailed regional boundaries and features
- **[🏰 Locations & Regions](overworld.json)** - Structured data about world locations
- **[⏰ Timeline Data](timeline.json)** - Raw event data in JSON format

## 🚀 Publishing & Local Workflow

1. **Make changes** to timeline, characters, or world data
2. **Test locally**: `python utils/lint_story.py`
3. **Commit and push** to trigger automatic publication
4. **Manual publication**: Use GitHub Actions → "CI" → "Run workflow"

**Manual Code Quality Commands:**
```bash
python -m black ./utils --line-length 88
python -m isort ./utils --profile black
python -m autoflake --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports ./utils/*.py
python -m pyupgrade --py39-plus ./utils/*.py
python -m flake8 ./utils/*.py
```

**Run Utility Scripts:**
- Lint and validate story data: `python utils/lint_story.py`
- Generate timeline summary and Mermaid diagram: `python utils/generate_timeline_mermaid.py`
- Generate timeline (JSON): `python utils/generate_timeline.py`
- Simulate species evolution: `python utils/evolve_species.py`
- Generate maps: `python utils/generate_map.py`
- Process story snippets (requires Ollama running locally): `python utils/snippet_processor.py`

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