# South of Tethys Publishing Workflow

This document describes how to publish the South of Tethys book artifacts and documentation.

## Overview

The South of Tethys repository uses GitHub Actions to automatically generate and publish various artifacts that comprise the "book" - a collection of visualizations, maps, timelines, and narrative summaries that represent the current state of the world.

## Artifacts Generated

### 1. Timeline Artifacts
- **Timeline Summary** (`timeline_summary.md`) - Human-readable chronological summary of all events
- **Timeline Mermaid Diagram** (`timeline_mermaid.md`) - Visual flowchart of event progression
- **Full Timeline Data** (`timeline.json`) - Complete structured timeline data

### 2. World Map Artifacts  
- **Interactive Map** (`interactive_map.html`) - Browsable map with clickable regions
- **Overworld Data** (`overworld.json`) - Structured region and location data
- **Geographic Data** (`regions.geojson`) - GeoJSON formatted geographic boundaries

### 3. Character & Species Data
- Character profiles and genealogy information
- Species evolution chains and trait information

## Automatic Publishing

### Triggers
The publishing workflow runs automatically on:

1. **Push to main branch** - Full publication
2. **Push to book-publish branch** - Full publication for testing
3. **Push to feature/* branches** - Artifact generation only (no deployment)
4. **Pull Requests** - Validation and artifact generation for review

### Manual Publishing
You can manually trigger a complete publication:

1. Go to the [Actions tab](../../actions) in GitHub
2. Select "CI" workflow
3. Click "Run workflow"
4. Select the branch (usually `main` or `book-publish`)
5. Check "Publish complete book artifacts" if you want full deployment
6. Click "Run workflow"

## Accessing Published Content

### GitHub Pages
Published documentation is available at: `https://lordlebu.github.io/SouthOfTethys/`

Available pages:
- **Main Timeline**: [index.md](https://lordlebu.github.io/SouthOfTethys/) 
- **Visual Timeline**: [timeline_mermaid.md](https://lordlebu.github.io/SouthOfTethys/timeline_mermaid.html)
- **Interactive Map**: [interactive_map.html](https://lordlebu.github.io/SouthOfTethys/interactive_map.html)

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
   
   # Generate maps
   python utils/generate_map.py
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
   python utils/generate_map.py
   
   # Commit results
   git add timeline/ cartography/
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
   - Ensure `cartography/regions.geojson` is valid GeoJSON
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
├── docs/                      # Published documentation (auto-generated)
├── timeline/                  # Timeline data and generated summaries
├── cartography/              # Maps and geographic data
├── characters/               # Character profiles and genealogy
├── flora_fauna/             # Species and evolution data
├── utils/                   # Publishing and generation scripts
└── requirements.txt         # Python dependencies
```

## Script Reference

- **`utils/lint_story.py`** - Validates data consistency and references
- **`utils/generate_timeline_mermaid.py`** - Creates timeline visualizations
- **`utils/generate_timeline.py`** - Processes and sorts timeline data
- **`utils/generate_map.py`** - Creates interactive maps
- **`utils/snippet_processor.py`** - Processes story snippets using LLM