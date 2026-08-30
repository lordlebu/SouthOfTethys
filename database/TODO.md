# database/ TODO

## Flora / fauna
- [x] Batch expansion v0.9.0 (8 flora, 8 fauna)
- [ ] Further subspecies as needed

## Missing P1 structure
- [ ] settlement_narmada_university — `place_narmada_university_library` exists and inherits its
      position from the Narmada field map. A settlement entity would give the campus itself a home.
- [ ] faction_narmada_scholars — Onko, Digha and Varuna all sit in academic circles with nothing
      declaring the circle. Would take the memory map from 3 factions to 4 and claim several of
      the characters currently grouped by culture alone.

## Story / events (deferred)
- [x] Event: Vijaya / Mask of Tethys offer — closed by putting Vijaya and the Yaksha Envoy into
      `event_tendua_crisis`, which is where his own notes already said he arrives. A separate
      event was not needed; the participants list was.

## Cross-ref hygiene
- [x] Audit event `location` fields (free-text vs settlement IDs). Five held bare strings —
      `ironfang_mountains`, `ancient_courts`, `hyrkanian_steppe`, `black_lotus_camp`,
      `upriver_exile_settlement` — which are now `place` entities. It was not closable before
      because there was no noun for somewhere named that a player cannot stand in. The linter
      now resolves `location` and `field_map` by field *name*, since a bare string is not
      id-shaped and the generic reference check could never see it.

## Field diary — schema gaps
See `docs/decisions.md` for the reasoning behind each.
- [x] `climate` on field maps — Lothal and Narmada each have their own sky
- [x] full_moon / flood: never generated, and check_playability now fails a rung that waits on either
- [ ] Decide where `full_moon` lives permanently — it is in the `weather` enum but is a lunar phase, not
      weather, and is deliberately never generated
- [x] `lava_field` — the Ganges Lava Sea now names it, and so do the 36 species that were
      filed under `mountains`
- [ ] Make `lava_field` renderable: it needs a tile texture before anything can stand on it,
      which is an art call. Species keep `mountains` alongside it until then.

## Field diary — content
- [x] A second field map — the Narmada Plateau, joined to Lothal by `neighbours`
- [x] Third and fourth field maps — Dwarka and the Dry Harbour
- [x] The Dry Harbour retired again: no story in it, and its Glass Scar and Caravan
      Ground moved to Dwarka. Three maps now. See `docs/decisions.md`.
- [ ] Fifth: the Shattered Sea is the only region buildable today without new art
- [ ] region_aravali records no biomes, so nothing can be laid out in it (Gedrosian had the
      same problem and was fixed by recording them)

## Index
Current: v1.13.0 — bump on each entity batch. This line said v1.9.0 for two releases;
`database/index.json` is the manifest and this is a pointer to it, so when they disagree
the index is right.
Field diary types: 3 field maps, 20 points of interest,
31 discoveries, 7 field questions, 8 NPCs,
8 vocabulary across three languages.

## Left open at the end of the memory-map programme (2026-08-30)

**Five places named but unplaceable.** `place_ancient_courts`, `place_gondwana`,
`place_grassland_sanctuary`, `place_ironfang_mountains`, `place_island_of_lund`. Each needs a
`within` naming what contains it, or its own coordinates. Guessing a container is authoring
geography, so these wait for a ruling rather than a commit.

**Five characters present at nothing.** Kubera, Lira, Aurum Theophanes, Shakariman, and Mitra of
the Oath. The first four have hooks in their own notes and no event to hang them on --
Shakariman's discovery of the arboreal octopus is the most obvious missing event. Mitra of the
Oath is different and deliberate: the Chess of Fate myth does not include him, so putting him at
the First Cosmic Move would be inventing his role rather than recording it.

**One event with no cast.** `event_battered_ekranoplan_ice_wall_voyage` — its source says a
nameless crew. It draws in the timeline and not in the memory map, which is the honest outcome.

**Four events with no causal edge.** The Aravali Massacre, the Kelpfang's final voyage, the
Primordial Union, and the Dragon's Spine (which is a retained test fixture and correctly isolated).

## Map generation — from the 2026-08-31 pass

- [x] Rivers rebuilt on Priority-Flood + D4 flow accumulation, the standard hydrology model.
      They converge, tributaries join, and every course reaches water because the filled surface
      has no minima to trap one. Replaced ninety greedy downhill walks from the highest ground,
      which is what braided the middle of the delta.
- [x] `field_map_narmada` gained `river`. The map is named for a river and had none: the
      generator carved channels and `applyPalette` erased every one, leaving ten named
      watercourses pointing at hills.
- [ ] **Replace `BECOMES` with a constrained classifier.** Generating a whole continent and then
      remapping it into a field map's palette is bespoke to this project and is the weakest thing
      in the generator. Three faults came out of it in one afternoon: marsh reclassified to
      watercourse, a plateau's rim reclassified to watercourse, and the same rim reclassified to
      hill. The standard answer is to hand `classifyBiome` the biomes a map is allowed to use so
      the thresholds divide the range among those, and nothing is ever generated that has to be
      substituted afterwards. Until then every ordering in that table is load-bearing and all
      three maps must be measured after touching one.
- [ ] Narmada's river is wider than a river. `carveRivers` cuts about 3% of that map and
      `routes.ts` eases wetland to river along every path between its six places; two sources,
      no single knob. Belongs with the rewrite above rather than another tuning pass.
- [ ] Canyons on the Narmada plateau, and cliffs on a delta. Both are wanted and neither is
      expressible today: `relief` bends elevation and moisture and says nothing about relief in
      the visual sense.

## Art, and what is blocked on it

- [ ] Tiles for `lava_field`, the sky biomes, and train track. All three wait on source art --
      `tools/build-terrain.js` converts drawn art into sheets, it does not invent it. The canon
      half of `lava_field` is nearly done: 36 species already name it and 29 are `encounter`.
- [ ] Marks for the making layer. Materials, items and vehicles have no art at all; the satchel
      panel is text. `src/ui/SpeciesIcon.tsx` is the pattern -- canon states the fact, the game
      picks the glyph, and an exhaustive `Record` makes a missing one a build failure.

## Content wanted

- [ ] Indian food: *choddo shak* (fourteen greens, Bengali), and fruits, vegetables and spices
      beyond them. Then the dishes as `items` + `recipes` + `foodways`, which is what the making
      layer was built for. New species take a trailing `source_index` so array order is safe.
- [ ] Indian vehicles: a Harappan cart and the Sinauli chariot, both well attested and both
      fitting `epoch_civilization_dawn`.

