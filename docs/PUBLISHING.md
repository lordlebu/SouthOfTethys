# South of Tethys Publishing Workflow

This document describes how to publish the South of Tethys book artifacts and documentation.

## Overview

The South of Tethys repository uses GitHub Actions to automatically generate and publish various artifacts that comprise the "book" - a collection of visualizations, maps, timelines, and narrative summaries that represent the current state of the world.

## Artifacts Generated

### 1. Timeline Artifacts

Written straight into `docs/` by the generators. There is no intermediate build directory:
the copy between the two is what went stale, and served another project's story for months.

- **Timeline Summary** (`docs/index.md`) - Every event, by epoch and then by cause
- **Timeline Mermaid Diagram** (`docs/timeline_mermaid.md`) - The epochs, and the causal graph
- **Full Timeline Data** (`docs/timeline.json`) - Complete structured timeline data

### 2. World Map Artifacts

None. The map pipeline was removed: it produced another project's geography, and `folium`
wants real lat/lon that canon does not have. See `docs/canon-integrity-plan.md`.

### 3. Character & Species Data
- Character profiles and genealogy information
- Species evolution chains and trait information

## Automatic Publishing

### Triggers

**One workflow publishes the book: `jekyll-gh-pages.yml`.** It runs a real Jekyll build over
`docs/` on any push to `main` that touches it.

`ci.yml` validates and generates, and deliberately does **not** deploy. It used to, and the two
raced for the same `github-pages` environment while publishing different things — `ci.yml`
uploaded the directory with no build at all, so it served raw markdown and ignored `_config.yml`,
the nav and `_includes/`. Whichever finished last decided whether the live site was a built site
or a folder of `.md` files. See `docs/decisions.md`.

`docs/` is tracked, so **what is committed is what gets published**. Regenerate before you
commit:

```bash
python utils/generate_timeline.py
python utils/generate_timeline_mermaid.py
python utils/generate_atlas.py
```

### Manual Publishing

Go to the [Actions tab](../../actions), select **"Deploy Jekyll with GitHub Pages dependencies
preinstalled"**, and run it on `main`. It rebuilds from whatever `docs/` currently holds.

## Accessing Published Content

### GitHub Pages
Published documentation is available at: `https://lordlebu.github.io/SouthOfTethys/`

Available pages:
- **Main Timeline**: [index.md](https://lordlebu.github.io/SouthOfTethys/) 
- **Visual Timeline**: [timeline_mermaid.md](https://lordlebu.github.io/SouthOfTethys/timeline_mermaid.html)

### GitHub Releases
For each publication, artifacts are also available as downloadable files in the workflow runs:

1. Go to [Actions tab](../../actions)
2. Click on the most recent successful "CI" run
3. Scroll down to "Artifacts" section
4. Download individual artifacts as needed

## Development Workflow

### For Contributors

1. **Make changes** to timeline, characters, or world data
2. **Test locally**:
   ```bash
   # Validate data consistency
   python utils/lint_story.py
   
   # Generate timeline visualizations
   python utils/generate_timeline_mermaid.py
   ```

3. **Commit and push** to a feature branch
4. **Create Pull Request** - This will trigger artifact generation for review
5. **Merge to main** - This will trigger full publication

### For Maintainers

#### Publishing a New Release
1. Ensure all content is ready on `main` branch
2. Create and push the `book-publish` branch for testing:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b book-publish
   git push origin book-publish
   ```
3. Verify artifacts are generated correctly
4. Merge `book-publish` back to `main` for final publication

#### Emergency Publication
If you need to publish immediately without waiting for the normal workflow:

1. Manual trigger via GitHub Actions (see "Manual Publishing" above)
2. Or run scripts locally and commit results:
   ```bash
   # Generate all artifacts
   python utils/generate_timeline_mermaid.py
   python utils/generate_timeline.py

   # Commit results
   git add docs/
   git commit -m "Manual artifact generation"
   git push
   ```

## Troubleshooting

### Common Issues

1. **Workflow fails on linting**
   - Check output of `python utils/lint_story.py`
   - Fix any data consistency issues before pushing

2. **Missing dependencies**
   - Ensure all required packages are in `requirements.txt`
   - Test locally: `pip install -r requirements.txt`

3. **GitHub Pages not updating**
   - Check that the workflow completed successfully
   - Pages may take a few minutes to update after deployment
   - Verify Pages is enabled in repository settings

4. **Maps not generating**
   - Check that `folium` is installed and working

### Getting Help

1. Check the [workflow logs](../../actions) for specific error messages
2. Test scripts locally to reproduce issues
3. Create an issue with error details and steps to reproduce

## File Structure

```
├── .github/workflows/
│   ├── ci.yml                 # Main publishing workflow
│   └── story-validation.yml   # Validation workflow
├── docs/                      # Published book, and where the generators write
├── database/                  # ALL canon: one JSON file per entity, plus schemas
├── services/                  # Retrieval API and the Chroma indexer
├── utils/                     # Validation, export and generation scripts
└── requirements.txt           # Python dependencies
```

## Script Reference

- **`utils/lint_story.py`** - Validates data consistency and references
- **`utils/generate_timeline_mermaid.py`** - Creates timeline visualizations
- **`utils/generate_timeline.py`** - Processes and sorts timeline data
- **`utils/check_playability.py`** - Simulates a playthrough; fails on content nobody can reach
- **`utils/export_canon_bundle.py`** - Writes the game's `data/canon/` bundle and its lock

`characters/` and `flora_fauna/` used to appear in this tree. They were placeholder directories,
removed when everything moved into `database/`, and `utils/snippet_processor.py` went with the
Ollama workflow it belonged to.