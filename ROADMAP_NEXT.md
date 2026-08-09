# Next Work Package

## Status

### 1. Canon cleanup + CI retarget — DONE (PR #21)

### 2. Validation hardening — partial
- [x] `utils/lint_story.py` validates `database/index.json` + files + cross-refs
- [x] Story validation CI hard-fails on lint errors
- [ ] Optional JSON Schema validation against `database/schemas/`

### 3. Chroma wiring — DONE (this branch)
- [x] Indexer reads `database/**/*.json`
- [x] Metadata carries `entity_id`, `entity_type`, `name`/`title`, `epoch`, `culture`
- [x] Incremental script prefers `database/` paths
- [x] Ported every call site off the removed pre-0.4 `chroma_db_impl` Settings API
- [x] Portal smoke-test against live Chroma (manual / local) — "Ask the canon" panel;
      headless equivalent is `scripts/query_chroma.py --expect`

### 4. Selective expansion — in progress
- [x] P0: `artifact_mask_of_tethys`
- [x] P0: `artifact_mask_of_sunlit_stone`
- [ ] P1: `settlement_narmada_university`
- [ ] P1: `faction_narmada_scholars`
- [ ] Event: Vijaya / Mask of Tethys offer

### 5. Still open
- Event graph: Vijaya arrival node
- More flora as needed
- Style debt pass (ruff BLE001/E501) when convenient
