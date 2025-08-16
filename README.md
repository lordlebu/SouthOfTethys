
# South of Tethys - Procedural Storytelling Engine

A procedurally evolving storytelling engine inspired by world simulation games like **Dwarf Fortress**. This project manages story events, character genealogy, and evolving flora/fauna in a version-controlled Git repository.

## 📖 Published Book & Artifacts

The complete "book" of South of Tethys is automatically published with each update:

- **📚 [View Published Book](https://lordlebu.github.io/SouthOfTethys/)** - Complete timeline, maps, and world data
- **🗺️ [Interactive World Map](https://lordlebu.github.io/SouthOfTethys/interactive_map.html)** - Explore the world geography
- **📊 [Visual Timeline](https://lordlebu.github.io/SouthOfTethys/timeline_mermaid.html)** - Event progression flowchart

### 🚀 Publishing Your Changes

1. **Make changes** to timeline, characters, or world data
2. **Test locally**: `python utils/lint_story.py`
3. **Commit and push** to trigger automatic publication
4. **Manual publication**: Use [GitHub Actions](../../actions) → "CI" → "Run workflow"

See **[📋 Publishing Workflow Guide](docs/PUBLISHING.md)** for complete instructions.

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

### Manual Code Quality Commands

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

### Recommended Minimal Setup
For most Python projects, start with:

- `black` (formatting)
- `isort` (imports)
- `flake8` (linting)
- `pre-commit-hooks` (basic hygiene)

Add `mypy`, `bandit`, and others as your codebase grows or if you need stricter checks.

# Chronology of Jambudweepa  
*From Primordial Seas to City-States*  

---

## ⏳ **Prehistoric Foundations**  
### (c. 500–250 Million Years Ago)  
- **Invertebrate Dominion**:  
  Ammonoids rule shallow seas. The **Ammonite Man** emerges as first spiritual entity - a cephalopod sage whispering through coral reefs.  
- **Avian-Synapsid Epoch**:  
  Flightless therapod birds and sail-backed synapsids dominate landmasses. **Owlman** appears as nocturnal guardian of forests.  

---

## 🐒 **Age of Vanaras**  
### (c. 50–5 Million Years Ago)  
1. **Vanara Zenith**:  
   - Proto-primates develop tool use and fire mastery in **Gondwana forests**  
   - Build tree-cities in the **Nilgiri Canopy** (southern Jambudweepa)  
2. **Great Devolvement**:  
   - Climate shifts fracture civilization  
   - Descendants regress to modern monkeys  
   - **Lionman** appears as sun-spirit guiding scattered tribes  

---

## 🚶 **Human Migrations**  
*(Wave Settlement Pattern: Northwest → East/South)*  

| **Era**         | **Group**       | **Origin**          | **Settlement**          | **Key Traits**                  |  
|-----------------|-----------------|---------------------|-------------------------|---------------------------------|  
| c. 50,000 BCE | **Jharwa**      | Zagros Mountains    | Saraswati Delta         | Cave painters, shell worshippers |  
| c. 10,000 BCE | **Vedda**       | Caspian Steppes     | Ganges Plain            | Horse tamers, fire ritualists    |  
| c. 5,000 BCE  | **Naga**        | Indus Valley        | Deccan Plateau          | Serpent cults, metalworkers      |  
| c. 3,000 BCE  | **Outliers**    | Hybrid populations  | Fringe regions          | Vanara-human mixes, bird-speakers |  

---

## 🌀 **Spiritual Beings & Gates**  
### (Timeless Entities)  
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

## 🏺 **Civilization Dawn**  
### (c. 3000–500 BCE)  
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

## 👁️‍🗨️ **Current Era** (c. 500 BCE–Present)  
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