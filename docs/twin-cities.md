# The Saraswati twin cities — 14 November 2026


## Approved terrain and final graphics checkpoint - 18 November 2026

The owner selected **A - Muted sage** for the northeastern cave meadow and hills after reviewing
three in-game samples. Lichen and olive remain development review alternatives. Sparse broad
NES pixel turf/stone patterns replace the bright flat mint. Stepped height/riverbank shading and
an earthy, irregular transition on both sides soften desert/grass, hill, mountain and snow edges.

This is game-owned presentation: one shared ground atlas, baked once, still one ground image per
tile. It replaces flat hill/bank outlines while preserving real cliff faces, bridges, buildings,
the accepted Beedu, world generation and saves. The review seed uses 521 frames / 2.125 MiB.
Mirlepa/Yamantaka retain their 120-second turns and very slow scene-time walks; generated cliff
shrubs, half-size border bushes, habitat decor and capped smoke/haze/river ripples are delivered.

Required illustration backlog: **0**. All 16 place views, 20 happening paintings, arrival/journey
art and main portraits are complete. Final integrated visual/gameplay/save/hardware-performance
review and owner review/merge remain; additional NPC sheets and seasonal variants are optional.
Software-renderer measurements remain noisy, particularly cave medians; they are not hardware-FPS
or zero-cost guarantees. No canon entities, language, version or export changes are needed.

Verified game implementation: [f80033e](https://github.com/lordlebu/4000BCESaraswathy/commit/f80033e41855650959e2f320575af14382971a3f).
Its checks passed **3,839 unit tests, eight combined browser cases**, typecheck, production build,
canon lock and bundle-size gates (app 217.1/220 KiB gzip). Hosted CI is tracked on the review PR
rather than treated as a permanent completed result in this document.

Read the [approved terrain decision and measurements](https://github.com/lordlebu/4000BCESaraswathy/blob/f80033e41855650959e2f320575af14382971a3f/docs/twin-terrain-softening.md),
[current completion audit](https://github.com/lordlebu/4000BCESaraswathy/blob/f80033e41855650959e2f320575af14382971a3f/docs/twin-cities-art-status.md),
[art-form guide](https://github.com/lordlebu/4000BCESaraswathy/blob/f80033e41855650959e2f320575af14382971a3f/docs/art-direction.md) and [original phased plan](https://github.com/lordlebu/4000BCESaraswathy/blob/f80033e41855650959e2f320575af14382971a3f/docs/twin-cities-art-plan.md).
Earlier dated counts and prompt briefs below are production history. All review captures and
raw generations remain in already ignored desktop paths. Game review: [PR #266](https://github.com/lordlebu/4000BCESaraswathy/pull/266).


## Landscape and motion polish - 18 November 2026

The new map now reuses suitable older-map grass/swamp/forest ground decor, with a compact
four-frame **nes jrpg sprite** shrub sheet. Regular bushes mark dry cliff lips; paired half-size
bushes soften grassland/desert borders. Placement is deterministic and capped, with routes,
bridges, buildings, courts and the cave's walking area clear.

Mirlepa and Yamantaka now exchange walking/seated roles every 120 seconds. Each walking turn
has one slow out-and-back, typically 20 seconds per tile, with a minimum of 12 seconds per tile.
Scene time drives their movement so the player's journey-time advances cannot speed it up.
Monthly props and visiting helpers retain their existing journey-day schedule.

The game adds simple three-frame river ripples, six blocky cave-hearth smoke puffs and small
localized desert haze, all using cached textures and camera/fog visibility gates. Effects update
at 5Hz; reduced-motion disables these optional marks. Their limits are 96 ripple marks, 12 haze
cells and six puffs. Software-renderer comparisons found no desert-haze regression, while cave
smoke readings remain noisy and need final hardware review. All five focused browser checks,
all 3,835 unit tests, typecheck, production build and size/data gates pass; the app remains
within 220 KiB gzip.

No required illustration production remains. Final integrated visual/gameplay/save/performance
review and owner review/merge remain; extra character sheets and seasonal variants are optional.
Existing buildings and accepted Beedu art are retained. This is presentation/documentation work,
with no new canon entities, languages, version, world generation or export changes.

Production commit: [0ca9ac7](https://github.com/lordlebu/4000BCESaraswathy/commit/0ca9ac74cf813459011fb71c7275dd4d2315b526).
The [exact prompts, budgets, checks and performance evidence](https://github.com/lordlebu/4000BCESaraswathy/blob/0ca9ac74cf813459011fb71c7275dd4d2315b526/docs/twin-landscape-motion-phase.md)
and [updated original plan](https://github.com/lordlebu/4000BCESaraswathy/blob/0ca9ac74cf813459011fb71c7275dd4d2315b526/docs/twin-cities-art-plan.md) live in the game repository.
Raw generations, screenshots and performance JSON stay in already ignored desktop paths.

## Place-view production complete ? 18 November 2026

The game delivers all fifteen remaining cozy watercolor place panoramas. With the accepted
Harappa courtyard, all sixteen twin-valley stops now have individual preferred views;
**no required illustrations remain**. New panels are full-colour 512?224 PNGs, crop/resize only,
with broader local palettes and authored features. The northeast cave shows green highlands,
a stream and mountain/snow layers; desert stops stay arid. The station scene was recomposed
so the ostrich and carriage remain visible in a shallow desktop card. Total new art: 3,677,562 bytes.

Production commit: [b568138](https://github.com/lordlebu/4000BCESaraswathy/commit/b568138d4625b87074f0fb91217f7dcfaf94eb37).
[Exact prompts, provenance and delivery ledger](https://github.com/lordlebu/4000BCESaraswathy/blob/b568138d4625b87074f0fb91217f7dcfaf94eb37/docs/twin-place-views-phase.md),
[current audit](https://github.com/lordlebu/4000BCESaraswathy/blob/b568138d4625b87074f0fb91217f7dcfaf94eb37/docs/twin-cities-art-status.md)
and [original plan](https://github.com/lordlebu/4000BCESaraswathy/blob/b568138d4625b87074f0fb91217f7dcfaf94eb37/docs/twin-cities-art-plan.md).

The next required phase is the final combined review: crops/readability and keyboard/touch,
fog/dusk, the cave household's turns/helpers/monthly props, Beedu flight/event/dialogue,
tram terminals, Kang's optional bust, save/reload and measured frame/load costs. Resolve findings,
then owner review/merge. Additional NPC replacements and seasonal variants remain optional.
Existing map buildings, simple NES direction and accepted Beedu are retained. This changes
presentation/documentation only: no new canon entities, languages, mechanics, version or export.
Large raw generations and screenshots remain in existing ignored desktop paths.

## Northeastern cave relocation — 18 November 2026

The Windward Cave household now lives in the northeastern highlands: a green meadow beside
a small mountain stream, with hills, bare mountains and border snowcaps. The northwest
Gedrosian margin remains desert. Mirlepa, Yamantaka, their helpers, discovery and conversations
retain their identities. The historical `poi_northwest_cave_camp` id remains for save compatibility.
The game owns its (51,12) placement and bounded saved-map migration. This canon correction
keeps v3.8.0 and re-exports the changed place/discovery with updated lock hashes; no new entities.
The graphics/relocation work merged in game PR #264 and lore PRs #170/#171.

## Graphics follow-up — 18 November 2026

The current game phase delivers nineteen new cozy watercolor event editions plus two journey
banners, using broader blue/teal/green/plum/coral palettes. All twenty valley happenings now
have preferred paintings. The actual map-entry/arrival page also has its own scene. Original
pixel editions remain retained fallbacks; new raw art and reviews remain ignored on desktop.

The existing mixture of building styles is explicitly accepted and stays untouched. Landscape
work reuses suitable older-map cliff/small-decor art and adds sparse generated **“nes jrpg sprite”**
cactus, flowering cactus, grass and stones. Roads, rail, courts and cave walking space stay clear.
The game also fixes unknown/known traveller portrait continuity and slows the ostrich tram's
viewing pace from 100 to 240ms/tile without changing canon, route, fare or gameplay day cost.

At this earlier checkpoint fifteen place views remained; the production phase above completes
them. Final integrated visual, likeness/reference and performance review remains required. The former 36-image backlog is reduced by this
completed twenty-one-image phase. Gameplay/culture/language data and building art are unchanged.
See the game's phase ledger and audited original plan linked below for exact completed/pending
items; this is a documentation synchronization, not a new canon release.
Production ledger: https://github.com/lordlebu/4000BCESaraswathy/blob/88a2ad5da0ede795183dc2c1c8415e8c9f026975/docs/twin-graphics-phase-2026-11-18.md.

## Colour and sculpture review — 17 November 2026

Future paintings should use a wider variety of colours and distinct scene palettes, with
indigo/blue/teal, green, plum and earth/cream accents and warm/cool separation. The cozy
watercolor style need not tint every material sepia. NES map art keeps simple pixel masses
and small ramps; no extra map detail or automatic repaint is requested. The linked external
chat's specific palette guidance has not yet been retrieved; these rules record the owner's
explicit instruction in the active game review.

The corrected Kang event cards keep all statue hair/beard/features visibly carved stone.
The carving-stage bust is unpainted; only the finished unveiling gets lapis lazuli eye inlays
and sparse ochre/indigo paint. These are game-owned illustration choices, not added canon
quest resources. At that earlier checkpoint the painting backlog was 36; the completed phase above leaves 15 place views.

## Current game art and phase checkpoint — 17 November 2026

The game now delivers Priest Kang in **light indigo**, with a named cozy watercolor conversation
portrait and separate carving/unveiling event paintings in the owner's supplied initial style.
His overworld identity and three life-size bust stages use **“nes jrpg sprite”**. The stone bust
stays sandstone. The optional five-beat commission remains the existing canon story; no second
quest or new event prose is required for the game-owned paintings.

Also delivered in the game: cave-local walking/alternating seated rests for Mirlepa and
Yamantaka; visiting helpers; monthly prayer-flag/Icmic-cooker/bonfire variants; generated NES
JRPG wildlife and ostrich tram; and Beedu's accepted small SNES flight/sighting/reaction layer.
Most people remain Harappan, with two Kia, Hutel Elamite, and the two named Denisovans; the
ethnicity/language/naming work is implemented. The existing world/canon division is unchanged.

The gameplay and event/travel-art phases are implemented; the current required visual backlog is
**15 place views**, followed by integrated visual/performance review and
exact-head CI/owner review. The eleven other existing NES NPC sheets and extra portrait/card
variations are optional replacement work, outside that count. See the game's
[audited phased inventory](https://github.com/lordlebu/4000BCESaraswathy/blob/88a2ad5da0ede795183dc2c1c8415e8c9f026975/docs/twin-cities-art-status.md)
and [original plan checkpoint](https://github.com/lordlebu/4000BCESaraswathy/blob/88a2ad5da0ede795183dc2c1c8415e8c9f026975/docs/twin-cities-art-plan.md).
Large raw generations and review screenshots remain in existing ignored desktop paths.

> **Current visual direction (17 November 2026):** The game owns presentation; follow its [element-by-element art guide](https://github.com/lordlebu/4000BCESaraswathy/blob/main/docs/art-direction.md). New overworld people, wandering animals and ostrich/emu trams explicitly use **“nes jrpg sprite”**. Terrain/buildings remain simple NES, Beedu alone keeps accepted small SNES art, and off-map faces/events/places/species plates keep their painted forms. Mirlepa/Yamantaka portraits alone use the approved anime treatment. These are presentation choices, not new cultural or biological canon.

The owner replaced the small-island proposal with a mainland journey between surviving
Harappa and Mohenjodaro. The theme is **cities becoming habitats**: occupied courtyard
homes beside nesting rooms, planted ruins and working water channels. These are living
remnants, with people maintaining parts of them, rather than abandoned archaeological exhibits.

Harappa is upstream on the west bank and uses ochre earthen architecture; Mohenjodaro is
downstream to the east and uses red fired brick. Arid ground and hills predominate, with the
Gedrosian desert margin to the northwest, greenery along the Saraswati, and the Tethys to
the southeast. The north–south river opens into a southern delta with coves. The new regional
reach does not rewrite the older locations or epochs of existing Gedrosian lore entities.

The initial authored content is twelve points of interest, eight discoveries, two field
questions, eight named NPCs and twelve happenings. Three named people also travel; the
game counts each once. Two random road companions and three temporary residents at one
rotating camp belong to the game's encounter layer. Helping with shade, drains and banks
comes from understanding discoveries, keeping the diary as progression. There is no new
homestead to build, combat or experience currency.

The game owns a 64×64 layout, separate road and railway on the causeway, and an ostrich-drawn
daytime tram. The latest owner correction requests each city's footprint to match Dwarka,
buildings to match existing hut scale, simple 8-bit NES artwork, and enclosures that combine walls
and natural features. Dimensions, collision, art and transport arithmetic belong to the game.

Canon v3.7.0 implements the first expansion within that allowance: Irekha, a reed-boat
repairer, and Ulenna, a cove watcher; the dune windbreak, reedwright bank and nesting cove;
and six quiet arrival/return happenings. Current totals are fifteen places, ten named people
and eighteen happenings, with the same eight discoveries and two questions. New locations
are linked reciprocally to existing discoveries. Further expansion uses the existing schemas
and diary progression. The game repository's `docs/twin-cities.md` records implementation phases,
actual screenshots, reproducible review commands and the improvement backlog.

Canon v3.8.0 adds the Windward Cave household, its discovery and welcome, the actual-flight
beedu happening, and Priest Kang's optional five-beat life-size bust commission. Current totals:
sixteen places, fifteen NPC identities (thirteen main people and two alternating helpers),
nine discoveries, two questions and twenty happenings. Mirlepa and Yamantaka are the only named
Denisovans; their household has Maru contacts without becoming a random Maru traveller pool.
Kang is a fictional descendant of the remembered Priest-King, whose archaeological reference
does not establish an actual historical royal or priestly office.

The thirteen main people are eight Harappans, two Kia, one Elamite (Hutel) and two Denisovans.
Culture and native/trade languages are recorded separately on the NPCs; the visiting cook is
Harappan and the visiting herder Kia. Hutel keeps the stable landingkeeper ID. Elamite naming
examples are fictional conventions, not asserted ancient vocabulary. Presentation and the
remaining art inventory are tracked in the game's original twin-city art plan; the current
coding phase does not mark that complete visual programme finished.
