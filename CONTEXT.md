# Project Context for GitHub Copilot

This project is a procedurally evolving storytelling engine inspired by world simulation games like **Dwarf Fortress**. It manages story events, character genealogy, and evolving flora/fauna in a version-controlled Git repository. All data is stored in JSON and Markdown files. The system must support:

---

## ✨ Objectives

- Maintain a **timeline** of world events (`timeline/timeline.json`)
- Track **characters** with structured metadata and genealogy (`characters/`)
- Record **species evolution** and traits (`flora_fauna/`)
- Connect each entity to **locations**, **art**, and **story arcs**
- Enable Python scripts to build, repair, and extend the world dynamically

---

## 🗂️ Folder Structure (Expected)

- `/timeline/` – Contains `timeline.json` with all world events sorted by Act/Scene
- `/characters/` – Character files (`.md` or `.json`) + a `genealogy.json` file
- `/flora_fauna/` – Species profiles and evolution chains
- `/locations/` – Descriptions of places in the world
- `/art/` – Physical or AI-transformed art references (sketches, paintings)
- `/utils/` – Python tools for timeline generation, genealogy tracking, species mutation
- `story_index.json` – High-level index of all characters, species, and events

---

## 🧠 Copilot Behavior Guidelines

- Assist in creating helper scripts to:
  - Parse and sort timeline entries
  - Link characters to events and genealogy trees
  - Simulate evolution of creatures over time
  - Detect lore inconsistencies or time shifts
- Use comments and structured metadata to inform decisions
- Favor clean, modular Python functions
- Encourage Markdown summary generation (for auto documentation)

---

## Example Tasks

- `generate_timeline.py` → Loads `timeline.json`, sorts by scene, prints summary
- `lineage_tracker.py` → Builds a family tree from `genealogy.json`
- `evolve_species.py` → Adds mutation stages to species based on events
- `generate_timeline_mermaid.py` → Creates visual timeline diagrams and summaries
- `generate_map.py` → Creates interactive HTML maps from geographic data
- `lint_story.py` → Validates story consistency and cross-references

## Publishing & Artifacts

The repository automatically generates and publishes "book" artifacts through GitHub Actions:

- **Timeline visualizations** (Mermaid diagrams, summaries)
- **Interactive maps** (HTML with geographic overlays)
- **Character and species data** (structured genealogy and evolution)
- **GitHub Pages deployment** for public viewing

### Manual Publication
- Use GitHub Actions manual trigger for immediate publishing
- All artifacts published to `https://lordlebu.github.io/SouthOfTethys/`
- Artifacts also available as downloadable files from workflow runs

### Development Workflow
1. Make changes to world data (timeline, characters, species, locations)
2. Run `utils/lint_story.py` to validate consistency
3. Commit and push - triggers automatic artifact generation
4. Merge to `main` branch for full publication

---

## Special Notes

- Dates are in fantasy format: "Act 1, Scene 2" or optionally a fictional calendar
- All updates should maintain consistency across the world
- Metadata keys are case-sensitive
- Art is linked by filename only, not embedded
