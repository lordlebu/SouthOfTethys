# Next Work Package

Branch: `feature/next-work-validation-chroma`  
Based on: main @ post-PR#19 (lore expansion v0.7.0)

## Context

`database/` is the structured canon (36 characters, 12 events, 19 fauna, 6 flora).
Legacy parallel stores (`characters/`, `flora_fauna/`, placeholder `timeline/`) still exist on main.
CI still points at those legacy paths.

## Work Items (ordered)

### 1. Finish canon cleanup (if PR #20 not merged)
- [ ] Remove `characters/` placeholders
- [ ] Remove `flora_fauna/` placeholders
- [ ] Remove legacy `timeline/*.json|md` placeholders
- [ ] Add `DESIGN.md` + update `CONTEXT.md` / `database/README.md`
- [ ] Retarget `utils/lint_story.py`, timeline generators, CI workflows to `database/`

### 2. Validation hardening
- [ ] Ship `utils/lint_story.py` that:
  - Loads `database/index.json`
  - Asserts every listed ID has a matching JSON file
  - Asserts counts match list lengths
  - Warns on dangling event cross-refs (`participants`, `predecessors`, `successors`, `artifacts`)
- [ ] Wire lint into CI as a hard fail (not `|| true`)
- [ ] Optional: JSON Schema validation against `database/schemas/`

### 3. Chroma wiring
- [ ] Update `utils/index_chroma.py` / `services/chroma` indexer to ingest `database/**/*.json`
- [ ] Map entity types → Chroma collections (characters, events, fauna, flora, mythology)
- [ ] Preserve stable IDs as vector metadata
- [ ] Smoke-test via Vidur Portal query against real Mask Family / Tendua lore

### 4. Selective canon expansion
Only add entities that unblock stories or tools:

| Priority | Entity | Why |
|----------|--------|-----|
| P0 | `artifact_mask_of_tethys` | Offered by Vijaya; plot-critical |
| P0 | `artifact_mask_of_sunlit_stone` | Named remaining Mask Family relic |
| P1 | `settlement_narmada_university` | Hub for Onko / Digha Jani era |
| P1 | `faction_narmada_scholars` | Groups current-era academics |
| P2 | More flora (Mahua, Shilajit Creeper, Whisper-Fig) | Ecology completeness |
| P2 | `character_kubera` | Linked to Vijaya / Tamralinga |

### 5. Event graph gaps
- [ ] Link `event_aravali_massacre` → later Mask Family migration if desired
- [ ] Add Vijaya arrival / Mask of Tethys offer as event node
- [ ] Optional: Narmada expedition events for current era

### 6. Out of scope this branch
- Full biological taxonomy rewrite
- New graph database
- Post-cataclysm hard lock
- Re-creating parallel entity folders

## Definition of Done

1. CI green on this branch
2. `python utils/lint_story.py` passes against `database/`
3. Chroma can retrieve at least one character + one event from canon
4. P0 artifacts present in `database/` + index updated

## Suggested commit sequence

1. cleanup + CI retarget (if needed)
2. validation script
3. chroma indexer changes
4. P0 artifacts + index bump
5. optional P1 settlements/factions
