# Register of Historical Events and Their Witnesses
*Collected papers of the Narmada University Collegium of Historical Inquiry — supplementary event concordance*

## I. The commission's purpose

The University distinguishes the lives of teachers and rulers from the later movements of their houses. This register accompanies chapters 03–07, 12 and 17–23 of the Harappan Convergence Chronicles. It covers only the migration-era court traditions, the Yadu and Bharata settlements, the eastern Bhṛgu inheritance and the southern Jharwa–Kia encounters discussed in those volumes.

The adopted manuscript chronology places Nārada in late Human Migrations, Urva and subsequently Aurva in Civilization Dawn, and Agasthya in the Age of Machinery. Exact years, unknown witnesses and undocumented routes are not supplied by conjecture.

## II. Existing archive entries

| Event | Epoch | Named participants / people | Editorial disposition |
|---|---|---|---|
| Battle of Ten Kings | epoch_migrations | character_sudas | Retain existing record |
| River Passage of the Bharata Force | epoch_migrations | character_sudas, character_visvamitra | Retain existing record |
| Viśvāmitra Lays Down His Seat | epoch_migrations | character_visvamitra | Retain existing record |
| Victory Recitals at the Bharata Court | epoch_migrations | character_vasistha, character_sudas | Retain existing record |
| Yadu Foundation of North Dwarka | epoch_civilization_dawn | Collective or unnamed | Retain existing record |
| Bharata Settlement at Hastinapura | epoch_civilization_dawn | Collective or unnamed | Retain existing record |
| Eastern Bhṛgu Teaching Reaches the Vedda Guilds | Unassigned | Collective or unnamed | Retain null; later inheritors, not the original ṛṣis |
| Jharwa Passage into the Yaksha South | Unassigned | Collective or unnamed | Propose epoch_migrations; exact generation unconfirmed |
| Agasthya’s Southern Exchange with the Yakshas | epoch_current | character_agasthya | Retain existing record |
| Chandraketugarh Garudasaur Blood Feud | epoch_current | Collective or unnamed | Retain existing record |

The existing Jharwa First-Wave & Shell Pact belongs to epoch_migrations. The Silvershore War, Founding of Lothal, Black Lotus Siege, Stone Pact and Tendua Crisis belong to epoch_civilization_dawn; their established participants and event graph remain untouched. These are contextual anchors, not new event proposals.

## III. Additional biographical event candidates

Divodāsa's frontier court and Nārada's witness vocation are broad biographical reconstructions, not independently attested single incidents. Urva and Aurva's successive teaching generations are adopted narrative placements. None implies a named meeting between these figures, a precise date or an invented locality. The proposed records below are draft candidates for editorial review.

## IV. Structured transcription schedule

The following JSON block is a machine-readable editorial handoff, not a live database or a claim that the existing linter already imports Markdown. The envelope separates existing IDs, proposed field changes, unresolved records and new candidate objects. Event objects use the existing event record field names. A future importer must validate against the actual schema and current repository, resolve references, check for duplicates and obtain approval before writing. Do not overwrite existing events or promote canon automatically. Null locations and empty participant lists are intentional; collective peoples are not fabricated character IDs. Character epoch synchronization is a separate task.

```json
{
  "retain_existing": [
    {
      "id": "event_battle_of_ten_kings",
      "epoch": "epoch_migrations",
      "participants": [
        "character_sudas"
      ],
      "location": null,
      "canon": "draft"
    },
    {
      "id": "event_sudas_river_passage",
      "epoch": "epoch_migrations",
      "participants": [
        "character_sudas",
        "character_visvamitra"
      ],
      "location": null,
      "canon": "draft"
    },
    {
      "id": "event_visvamitra_lays_down_his_seat",
      "epoch": "epoch_migrations",
      "participants": [
        "character_visvamitra"
      ],
      "location": null,
      "canon": "draft"
    },
    {
      "id": "event_vasistha_court_recitals",
      "epoch": "epoch_migrations",
      "participants": [
        "character_vasistha",
        "character_sudas"
      ],
      "location": null,
      "canon": "draft"
    },
    {
      "id": "event_yadu_foundation_north_dwarka",
      "epoch": "epoch_civilization_dawn",
      "participants": [],
      "location": "settlement_dwarka",
      "canon": "draft"
    },
    {
      "id": "event_bharata_settlement_hastinapura",
      "epoch": "epoch_civilization_dawn",
      "participants": [],
      "location": "place_hastinapura",
      "canon": "draft"
    },
    {
      "id": "event_agasthya_yaksha_southern_exchange",
      "epoch": "epoch_current",
      "participants": [
        "character_agasthya"
      ],
      "location": null,
      "canon": "draft"
    },
    {
      "id": "event_chandraketugarh_garudasaur_blood_feud",
      "epoch": "epoch_current",
      "participants": [],
      "location": "place_chandraketugarh",
      "canon": "secondary"
    }
  ],
  "proposed_updates": [
    {
      "id": "event_jharwa_passage_into_yaksha_south",
      "expected": {
        "epoch": null
      },
      "set": {
        "epoch": "epoch_migrations"
      },
      "status": "proposed",
      "reason": "Earlier Jharwa movement; migration-era placement recommended, not independently dated."
    }
  ],
  "deferred": [
    {
      "id": "event_bhrgu_teaching_enters_vedda_guilds",
      "epoch": null,
      "reason": "Later descendants entered existing Vedda guilds; exact epoch not established. Must precede or be established by the Age of Machinery blood feud."
    }
  ],
  "new_event_candidates": [
    {
      "type": "event",
      "id": "event_divodasa_frontier_court",
      "title": "Divodāsa and the Frontier Court",
      "epoch": "epoch_migrations",
      "participants": [
        "character_divodasa"
      ],
      "location": null,
      "predecessors": [],
      "successors": [],
      "summary": "The earlier royal figure is remembered in praise traditions. The University reconstructs his court as a mobile centre of passage obligations and arbitration; specific laws and victories are unconfirmed.",
      "canon": "draft",
      "sources": [
        "docs/books/narmada-university/harappan-convergence/03-divodasa-and-the-frontier.md"
      ]
    },
    {
      "type": "event",
      "id": "event_narada_travelling_witness_tradition",
      "title": "Nārada and the Travelling Witnesses",
      "epoch": "epoch_migrations",
      "participants": [
        "character_narada"
      ],
      "location": null,
      "predecessors": [],
      "successors": [],
      "summary": "The adopted late-migration portrait associates Nārada with itinerant testimony and Kāṇva recitation across political boundaries. No specific journey, court meeting or oath is attested.",
      "canon": "draft",
      "sources": [
        "docs/books/narmada-university/harappan-convergence/07-narada-and-the-witnesses.md"
      ]
    },
    {
      "type": "event",
      "id": "event_urva_eastern_bhrgu_teaching",
      "title": "Urva and the Eastern Bhṛgu Teaching Succession",
      "epoch": "epoch_civilization_dawn",
      "participants": [
        "character_urva"
      ],
      "location": null,
      "predecessors": [],
      "successors": [
        "event_aurva_garudasaur_blood_teaching"
      ],
      "summary": "Urva represents the earlier eastern teaching generation, carrying Bhṛgu knowledge of heat, vessels and preservation after the migration-era conflicts.",
      "canon": "draft",
      "sources": [
        "docs/books/narmada-university/harappan-convergence/19-aurva-urva-and-the-eastern-fire-houses.md"
      ]
    },
    {
      "type": "event",
      "id": "event_aurva_garudasaur_blood_teaching",
      "title": "Aurva and the Garudasaur Blood Tradition",
      "epoch": "epoch_civilization_dawn",
      "participants": [
        "character_aurva"
      ],
      "location": null,
      "predecessors": [
        "event_urva_eastern_bhrgu_teaching"
      ],
      "successors": [],
      "summary": "Aurva develops the eastern teaching tradition of obtaining and preserving Garudasaur blood. Later inheritors transmit it to Vedda guilds; no personal visit to Chandraketugarh or exact kinship is established.",
      "canon": "draft",
      "sources": [
        "docs/books/narmada-university/harappan-convergence/19-aurva-urva-and-the-eastern-fire-houses.md"
      ]
    }
  ]
}
```

## V. Chronological constraints

- Divodāsa precedes Sudās in the praise tradition; no exact succession or direct causal event edge is established.
- The existing Battle of Ten Kings precedes Vasiṣṭha's court recitals. The river passage and Viśvāmitra's renunciation remain unordered relative to the battle.
- North Dwarka's Yadu hegemony precedes Lothal's ascendancy; this does not establish an exact relation to Kavik's founding event. Bharata settlement at Hastinapura belongs to the opening of Civilization Dawn.
- Urva's teaching precedes Aurva's; their later inheritors reach Chandraketugarh before or by the documented industrial blood feud. The guild transfer itself remains undated. Garudasura moss denotes blood material, not the distinct moss flora.
- Jharwa southern passage precedes Agasthya's exchange. Yaksha sovereignty is preserved; no personal meeting with Kubera is implied.

## VI. University finding

The archive should preserve historical sequence without turning every institutional inheritance into a personal encounter. The proposed new entries remain draft, and the existing event records retain their original authority. The War of the Three Estuaries, Lothal Canal Compact and Lothal Guild Settlement are outside this commission's scope.
