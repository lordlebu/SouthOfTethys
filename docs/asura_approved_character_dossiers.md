# Approved Asura continuity — lore-only character dossiers and migration gates

**Decision date:** 2026-11-12. **Status:** approved authorial canon, with explicit provisional items. This document is a lore-only record; it does not create gameplay NPCs, change event participants, or expand the Asura-Tainted Princess.

## Vaishura — one individual, multiple offices

**Existing structured entity:** `character_commander_vaishura`. Commander of the Fang Vanguard, master breeder of the Underworld and Keeper of Forbidden Records are roles of **one Vaishura**, not two homonymous characters. The Keeper is associated in the conversation canon with the Danava tradition and the Triassic (~230 MYA); the Fang Vanguard story already belongs to the prehistoric epoch. Neither the order of offices nor the relationship of the Danava title to the existing `species: asura` is resolved. Keep `status: deceased`, the existing entity ID and all Fang War event links. Do not invent a second Vaishura.

## Manjalaya (Vishaili) — provisional death chronology

**Existing entity:** `character_manjalaya`. Asura princess summoned through Dwarka Gate by Varunesh during the late Deep Antiquity Shadow Pact. Their relationship weakened her powers and near-immortality according to the working narrative. An account describes her eventual peaceful death with Sarishne and Gagdji present, but **the chronology and chapter placement of this account are provisional**. Do not create a death event, assign a date, or change `status: mythic` until the chronology is settled. Her daughter is excluded from expansion.

## Sarishne — lore-only character dossier

**Name:** Sarishne  
**Lineage:** Rakshasa (not interchangeable with Asura, Danava, Daitya or Oni)  
**Role:** Wilderness protector associated with Tenduas  
**Chronology:** Witnessed the original late Deep Antiquity Shadow Pact in secret; later interacted with Manjalaya during a distinct migration-era Dwarka Gate disturbance  
**Relations:** Partner of Gagdji, an Oni  
**Later account:** Present at Manjalaya's peaceful death, whose date remains provisional  
**Unknown:** Birth/death status, exact dates, geographical coordinates and whether her concealed presence should be included in structured event participant lists  
**Record status:** Approved lore-only dossier; structured character JSON deferred until species taxonomy and index migration can be validated

## Gagdji — lore-only character dossier

**Name:** Gagdji  
**Lineage:** Oni (distinct from Rakshasa and Asura)  
**Relation:** Partner of Sarishne  
**Later account:** Present at Manjalaya's peaceful death, with chronology provisional  
**Unknown:** First appearance, age, dates, geographical coordinates and knowledge of the original Shadow Pact. Attendance at a later event does **not** establish knowledge of the original pact.  
**Record status:** Approved lore-only dossier; structured JSON deferred pending species taxonomy and index validation

## Kalyani — standalone lore-only character dossier

**Name:** Kalyani  
**Lineage:** Daitya (not synonymous with Asura or Danava)  
**Established relation:** Friendship with Vusajc Karthakur  
**Unknown:** Precise epoch, location, mortality status, powers, political affiliations and detailed events  
**Record status:** Approved standalone dossier; structured JSON deferred pending taxonomy and chronology evidence

## Vusajc Karthakur — standalone lore-only character dossier

**Name:** Vusajc Karthakur  
**Established relation:** Friend of Kalyani  
**Unknown:** Species, culture, epoch, location, mortality status, powers and detailed events. Do not infer that Vusajc is Daitya merely because Kalyani is.  
**Record status:** Approved standalone dossier; structured JSON deferred pending reliable species/epoch identification

## Dwarka Gate versus Ancient Courts — structural investigation

The late Deep Antiquity `event_shadow_pact` has `location: place_ancient_courts` even though its summary locates the summoning at a Dwarka Gate. `place_dwarka_gate` exists but its currently documented coordinates and epoch represent the **Age of Machinery**, not a known Deep Antiquity coordinate. The court's location remains unresolved.

**Investigation outcome:** The narrative location and the structured location are inconsistent in specificity. Changing `event_shadow_pact.location` to `place_dwarka_gate` could resolve the site reference, but would import an Age of Machinery georeference into a Deep Antiquity event without proof of stable coordinates and could affect event/location-dependent consumers. **Do not make this structural change yet.** A later migration-era Gate disturbance is distinct from the original Shadow Pact; whether it used the identical physical Gate remains unresolved. Preserve event graph, participants and the `curse_on_ancient_courts` outcome pending an explicit structural migration review.

## Asura-Tainted Princess — protected existing canon

Keep `character_asura_tainted_princess`, `npc_asura_princess`, related storyline, post-cataclysmic context, and all established narrative unchanged. No new story, supernatural abilities, relationships, knowledge or encounter. Correct only a direct contradiction if identified and separately reviewed.

## Schema and game isolation

`database/schemas/character.schema.json` permits optional `species`, `culture` and `epoch`, but `database/species.json` currently has **no** `rakshasa`, `oni`, `daitya` or `danava` entry; `database/cultures.json` also lacks corresponding classifications. `database/index.json` requires every structured character to be indexed, with accurate counts. A missing species could default to `human` in some consumers, which would be inaccurate. These four dossiers are therefore standalone lore-only records in this document, **not** incomplete JSON characters. Creating structured entities requires a separate taxonomy/count/index migration and a comparison of the generated game canon bundle.

No game code, game data, NPC, storyline, event dependency, map coordinate or deployment is authorized by this document. Before any PR, verify canon validation on the exact head and validate the game in an isolated checkout if available; otherwise report the limits of existing CI evidence.
