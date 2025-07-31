# GitHub Copilot Instructions for SouthOfTethys

## Project Overview
- **SouthOfTethys** is a procedurally evolving storytelling engine inspired by world simulation games (e.g., Dwarf Fortress).
- All world data is stored in JSON and Markdown files, version-controlled in Git.
- Python scripts in `utils/` automate worldbuilding, event tracking, genealogy, and species evolution.

## Architecture & Data Flow
- **Timeline**: All events are tracked in `timeline/timeline.json`, sorted by fantasy date (e.g., "Act 1, Scene 2").
- **Characters**: Each character has a `.json` or `.md` file in `characters/`, with genealogy tracked in `characters/genealogy.json`.
- **Species**: Flora/fauna profiles and evolution chains are in `flora_fauna/`.
- **Locations**: World regions and connections are described in `cartography/overworld.json` and `locations/`.
- **Art**: Referenced by filename only, not embedded.
- **Scripts**: Key Python tools include:
  - `generate_timeline.py`: Sorts and summarizes timeline events.
  - `lint_story.py`: Validates consistency, date formats, and cross-references (characters/species).
  - `generate_timeline_mermaid.py`: Outputs a pictorial timeline as Mermaid graph.
  - `evolve_species.py`: Simulates species mutation based on events.
  - `snippet_processor.py`: Uses LLMs (Ollama) to extract structured data from story snippets.

## Developer Workflows
- **Build & Validate**:
  - Use Docker (`Dockerfile`, `compose.yaml`) for reproducible builds and script execution.
  - Run `python utils/lint_story.py` to check for broken or inconsistent story data before commits.
  - CI/CD pipelines (`.github/workflows/ci.yml`, `story-validation.yml`) run linting, timeline generation, and publish artifacts on push/PR to `main` and `feature/*` branches.
- **Pre-commit Hook**:
  - `.git/hooks/pre-commit` runs auto-formatting (autopep8, autoflake) and flake8 linting before allowing commits.
- **Debugging**:
  - Use VS Code's Docker debug tasks (`.vscode/launch.json`, `compose.debug.yaml`) for step-through debugging in containers.

## Project-Specific Conventions
- **Fantasy Date Format**: All events use "Act X, Scene Y" format; scripts expect this for sorting and validation.
- **Metadata**: Keys are case-sensitive; art is referenced by filename only.
- **Consistency**: All updates must maintain world consistency; cross-file references (e.g., character/species in events) are validated by scripts.
- **Modular Python**: Scripts are organized for single-responsibility and composability.

## Integration Points
- **Ollama LLM**: `snippet_processor.py` connects to a local Ollama server to extract structured data from text snippets.
- **Artifacts**: Timeline visualizations and world maps are published as build artifacts in CI.

## Examples
- To add a new event: update `timeline/timeline.json` and run `generate_timeline.py` and `lint_story.py`.
- To add a new character: create a `.json` in `characters/`, update genealogy if needed, and validate with `lint_story.py`.
- To process a story snippet: run `snippet_processor.py` (requires Ollama running locally).

## Key Files & Directories
- `timeline/timeline.json`
- `characters/`
- `flora_fauna/`
- `cartography/overworld.json`
- `utils/`
- `.github/workflows/`
- `.vscode/`
- `Dockerfile`
- `compose.yaml`
- `CONTEXT.md`
---
**For AI agents:**
- Always validate cross-references and formats using provided scripts before committing or merging.
- Prefer updating or generating Markdown summaries for documentation.
- Use the fantasy date format and maintain consistency across all world data.

name: Upload merged timeline artifact
uses: actions/upload-artifact@v4
with:
  name: full_timeline
  path: timeline/timeline.json
