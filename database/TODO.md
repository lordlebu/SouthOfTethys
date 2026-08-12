# database/ TODO

## Flora / fauna
- [x] Batch expansion v0.9.0 (8 flora, 8 fauna)
- [ ] Further subspecies as needed

## Missing P1 structure
- [ ] settlement_narmada_university
- [ ] faction_narmada_scholars

## Story / events (deferred)
- [ ] Event: Vijaya / Mask of Tethys offer

## Cross-ref hygiene
- [ ] Audit event `location` fields (free-text vs settlement IDs)

## Field diary — schema gaps
See `docs/decisions.md` for the reasoning behind each.
- [ ] `climate` on field maps — weather weights are hardcoded in the game engine today, so
      every region shares one sky
- [ ] Decide where `full_moon` lives — it is in the `weather` enum but is a lunar phase, not
      weather, and is deliberately never generated
- [ ] Ladders are meant to run seven rungs; 7 of 9 discoveries run 3–5. Settle the target
      before authoring another region against the shorter shape
- [ ] `lava_field` biome is declared and nothing uses it — author for it or drop it

## Field diary — content
- [ ] A second field map. The overworld has one, so it has nothing to navigate.
- [ ] Region for it is an open creative call (see `docs/decisions.md`)

## Index
Current: v1.3.0 — bump on each entity batch.
Field diary types: 1 field map, 6 points of interest, 9 discoveries, 2 field questions,
3 NPCs, 3 vocabulary.
