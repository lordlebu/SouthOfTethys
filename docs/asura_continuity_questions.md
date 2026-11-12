# Asura and associated characters — continuity issues and canon questions

**Status:** Review draft; no new character, event, quest, game code, or mechanics authorized. This is a question register, not a canon amendment. Use the eight approved Pashupati–Jharwa decisions and the November 2026 conversation canon archive as working constraints. Older GitHub JSON is recorded faithfully, even where it disagrees.

## Issue 1 — Vaishura's identity and office (high priority)

**GitHub:** `character_commander_vaishura` is a deceased Asura, commander of the Fang Vanguard and master breeder of Permian synapsids; `event_asura_synapsid_domestication` associates him with the Fang Wars and the Dwarka Gate in the prehistoric epoch.

**Conversation account:** Vaishura is described as a Danava Keeper of Forbidden Records, associated with the Triassic (~230 MYA), and distinct from other Asura roles. The sources do not yet establish whether this is a different figure, a later/earlier office of the same figure, or a naming collision.

**Question V1:** Are Commander Vaishura and Keeper Vaishura (A) the same individual with two roles, (B) different individuals sharing a name, or (C) unresolved until a primary source is selected?

**Question V2 (only if A):** Is his Keeper office contemporaneous with, earlier than, or later than the Fang Vanguard? Preserve the existing death status unless explicitly revised.

**Implementation gate:** Do not rename, delete, merge or duplicate `character_commander_vaishura` until resolved. Do not change event participants or causality.

## Issue 2 — Manjalaya's life course and supernatural decline

**GitHub:** `character_manjalaya` is an Asura princess summoned by Varunesh, has `status: mythic`, and lists Varunesh as spouse and the Asura-Tainted Princess as child. The Shadow Pact is in Deep Antiquity.

**Conversation account:** The union gradually diminished Manjalaya's powers and near-immortality. During the migration-era Dwarka Gate disturbance, she and Sarishne cooperated and later shared private disclosures. A later account describes Manjalaya's peaceful death with Sarishne and Gagdji present, but the November 2026 chapter archive stops before that death. The two accounts therefore represent different narrative horizons, not proof that the death belongs to Chapter 20.

**Question M1:** Should `status: mythic` remain a classification of narrative attestation, or should Manjalaya's eventual mortality be represented separately in canon? Do not substitute `deceased` without checking what `status` means to the schema and consumers.

**Question M2:** Is the peaceful death an approved later event without a date, or should its timing remain uncommitted until a later chapter?

**Question M3:** How should the private disclosure be recorded without making it common knowledge to human eyewitnesses or to the daughter?

## Issue 3 — Sarishne and Gagdji: absent or unindexed characters

**Repository search:** No matching Sarishne or Gagdji character records were found in the initial default-branch code search; absence from search is not definitive proof of absence from every source.

**Conversation account:** Sarishne is a Rakshasa wilderness protector associated with Tenduas. She secretly witnessed the original Shadow Pact, did not intervene, and later met Manjalaya at a separate migration-era Gate disturbance. Gagdji is her Oni partner; the later peaceful-death account includes both.

**Question S1:** Should Sarishne and Gagdji receive new **lore-only** character entities now, or remain documented in prose pending source verification?

**Question S2:** Which cultural/species fields and chronological statuses are canonical for each? Do not equate Rakshasa, Oni, Asura, Danava and Daitya.

**Question S3:** Does Gagdji's attendance at Manjalaya's later death establish any earlier personal knowledge of the Shadow Pact? Default: no.

**Implementation gate:** Any new entity needs a valid schema, index maintenance, and reference checks. Do not add either character to `event_shadow_pact` participants without deciding whether a secret nonintervening witness belongs in that field.

## Issue 4 — Kalyani and the taxonomy of Asura-associated beings

**Repository search:** No matching Kalyani record was found in the initial code search.

**Conversation account:** Kalyani is a Daitya, associated with a friendship involving Vusajc Karthakur. That relationship should not be conflated with Vaishura's history or the Shadow Pact.

**Question K1:** Should Kalyani and Vusajc Karthakur be introduced as standalone historical characters now, or held for a dedicated Daitya-era audit?

**Question K2:** Does the existing character schema support Daitya and Danava as distinct species or cultures, or should the taxonomy be documented in prose first to avoid broad schema changes?

## Issue 5 — Two Dwarka Gate incidents and the location of the ancient court

**GitHub:** `event_shadow_pact` still references `place_ancient_courts`, while its summary places the summoning through Dwarka Gate. The ancient-courts description has been clarified, but the event location was intentionally left unchanged.

**Conversation account:** The late Deep Antiquity Shadow Pact and the migration-era accidental Gate disturbance are distinct. Whether the same physical Gate was involved remains unresolved. The court's exact location remains unresolved.

**Question G1:** Should the event's `location` remain a legacy court association with an explanatory note, or be updated to a separately validated Dwarka Gate place ID after confirming schema and existing geography?

**Question G2:** Should the migration-era disturbance be a new event record, or remain prose-only to avoid changing the game's event graph?

## Issue 6 — The Asura-Tainted Princess and game compatibility

**GitHub:** `character_asura_tainted_princess` is alive, has an existing field-diary NPC (`npc_asura_princess`) and storyline, and has extensive post-cataclysmic notes.

**Canon boundary:** Preserve the daughter's existing lore; do not add new plot, explanation of immortality, knowledge of Sarishne, or encounters.

**Question P1:** Should this character be **excluded from all modifications** except correction of direct contradictions? Recommended: yes.

## Safe implementation order and validation

1. Obtain explicit answers to V1, M1/M2, S1, K1/K2, G1/G2 and P1 before editing contested entities.
2. Keep proposed changes on `lore/pashupati-jharwa-eight-decision-audit`; prefer prose-only corrections before new structured entities.
3. Do not edit `lordlebu/4000BCESaraswathy`, its generated `data/canon/` bundle, game code, save schema, NPCs, quests, discovery prerequisites or content adapters.
4. Run canon validation (`python utils/lint_story.py`, `python utils/check_playability.py`) on the branch. Inspect the diff and any exported-data changes.
5. **At the end**, validate the game in a separate, read-only checkout if available: `npm ci`, `npm run check:data`, `npm run typecheck`, `npm test`, `npm run build`, `npm run check:size`, and relevant `npm run test:e2e`. If the game checkout or test environment is unavailable, state that explicitly; do not claim a passing game run.
6. No PR merge or deployment without a further explicit approval.
