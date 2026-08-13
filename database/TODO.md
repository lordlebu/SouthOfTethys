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
- [ ] Fifth: the Shattered Sea is the only region buildable today without new art
- [ ] region_aravali records no biomes, so nothing can be laid out in it (Gedrosian had the
      same problem and was fixed by recording them)

## Index
Current: v1.6.0 — bump on each entity batch.
Field diary types: 4 field maps, 24 points of interest,
31 discoveries, 8 field questions, 10 NPCs,
10 vocabulary across three languages.
