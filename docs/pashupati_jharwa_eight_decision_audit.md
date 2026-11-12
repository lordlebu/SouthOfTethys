# Pashupati–Jharwa historical reconciliation — eight approved decisions

Status: approved historical rulings, staged for review on an isolated lore branch. No game changes or deployment authorized.

## Decisions

1. Elder Repa founded the first **documented Jharwa** settlement in the Saraswati Delta, not the first human settlement. Preserve the Shell Pact and the Ammonite Man.
2. Pashupati Chakravarthy's court was on Jambhudweepa, but its precise location is **unresolved**. Do not infer a location from Dwarka Gate.
3. Ritual competence declined through **generational loss of knowledge**: restricted transmission, memorized forms without full understanding, and weakened mastery. No hereditary curse is required.
4. Expanding Jharwa settlements displaced pre-Jharwa communities, which eventually disappeared **as distinct societies**. Do not infer total biological extinction, a single war, or systematic extermination.
5. Ritual gestures, chants, and oral accounts survived in fragments among later communities, including some Jharwa settlements. Full meanings and supernatural efficacy were largely lost.
6. The weakening court survived for **several generations after the first Jharwa arrivals**; its exact dissolution date is unresolved.
7. Varunesh (Tukulti-Vishra) is **deceased**. The date, place, and circumstances of death are unknown.
8. Fragmentary archaeological traces and conflicting oral traditions of the old court survive. The underlying historical events are true in authorial canon, even where later witnesses disagree.

## Historical boundaries

Pashupati and Varunesh belonged to an older, pre-Jharwa human population. The identity, arrival route, and dates of that population are not established. The ancient court possessed nature-bound rites acquired through contact with intelligent surviving Vanaras, but not advanced urban technology. Varunesh's Shadow Pact occurred in late Deep Antiquity, before the Jharwa major migration, at the preexisting Dwarka Gate. The Shadow Pact summoned Manjalaya; it did not enslave or control her. No expansion of the Asura-Tainted Princess's lore is authorized.

## Repository conflicts requiring careful reconciliation

- `database/events/event_jharwa_first_wave_shell_pact.json`: outcome currently says "first human settlement in the Saraswati Delta". Replace **only this claim** with "first documented Jharwa settlement in the Saraswati Delta" when implementing; preserve event ID, epoch, participants, predecessors, successors, Shell Pact and other fields.
- `database/events/event_shadow_pact.json`: location is `place_ancient_courts`, although the event narrative says Varunesh used a Dwarka Gate. `database/places/place_ancient_courts.json` calls the court the seat where the pact was made. **Do not silently relocate either place**. Review whether the event location encodes the court, the gate, or a historical association before any structural correction.
- `event_shadow_pact.json` outcome `curse_on_ancient_courts` and older narrative portrayals of a cursed dynasty: retain existing supernatural story pending review, but do **not** treat the curse as the cause of inherited ritual incompetence. The accepted cause is generational knowledge loss.
- `database/characters/character_varunesh.json`: `status: deceased` agrees with decision 7; do not add a death scene.
- `database/TODO.md` already lists `place_ancient_courts` as unplaced. Preserve that uncertainty.
- Existing generated `docs/` views and `AI_CONTEXT.md` may repeat older wording. Inspect source-of-truth and generation process before modifying them; do not hand-edit generated artifacts.

## Isolation and regression gates

- This branch is for lore-only review. **Never edit `lordlebu/4000BCESaraswathy`** as part of this reconciliation.
- Preserve all unrelated characters, migrations, cultures, geography, events, and game discoveries. Do not change identifiers, event dependency edges, discovery prerequisites, epochs, or coordinates merely to express historical prose.
- Before any pull request, inspect the final diff and branch head, run `python utils/lint_story.py` and `python utils/check_playability.py` against the actual modified canon checkout.
- If a canon export consumed by the game changes, compare the generated bundle and run the game's `npm run check:data`, `npm run typecheck`, `npm test`, `npm run build`, `npm run check:size` and relevant `npm run test:e2e` in a non-deploying test environment. Do not commit generated bundles or game code.
- A passing lore-only review does **not** imply that game regression tests have run. No merge or deployment without separate explicit authorization.
