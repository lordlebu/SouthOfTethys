# The Timeline of South of Tethys

<p class="book-nav"><a href="https://lordlebu.github.io/SouthOfTethys/">The Timeline</a> &middot; <strong>Epochs &amp; Events</strong> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/atlas.html">The Atlas</a> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/memory_map.html">The Memory Map</a> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/bestiary.html">The Bestiary</a> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/cookbook.html">The Cookbook</a></p>

_Generated from `database/events/` and `database/timeline/epochs.json` by `utils/generate_timeline_mermaid.py`. Do not edit by hand._

## The epochs

```mermaid
timeline
    title South of Tethys — the epochs
    section Prehistoric Foundations & Age of Vanaras
        500 MYA – 5 MYA : The Curse of the Hollow Trees : The Turning of Kunti Against the Seedbearer : The Planting of the Moon-Seed : The Establishment of the Womb Rites : The First Move of the Chess of Fate : The Fang vs. Scale Wars : The Domestication of the Fang Vanguard : The Asura Gondwana Intervention
    section Deep Antiquity
        before the migrations : The Battle of Mohenjodaro : Forging of the Dragon’s Spine (sample) : The Great Devolvement : Shadow Pact of Saraswati : The Primordial Union under the Asura Planet
    section Era of Human Migrations
        50K – 5K years ago : Aravali Massacre & Sanctuary : Battle of Ten Kings (draft) : The Botai Cattle Raid : Dispute over Inherited Household Obligations (draft) : The Jharwa First-Wave & The Shell Pact : Opening of the Naraka Lok Portal : The Narmada Apothecary Herb Quest : The Retreat of Owlman : Sarishne Encounters Manjalaya at a Gate Disturbance (draft) : River Passage of the Bharata Force (draft) : Victory Recitals at the Bharata Court (draft) : Viśvāmitra Lays Down His Seat (draft) : Wiznu and Aryaman Appeal to the Thunder-Bearer (draft)
    section Civilization Dawn (Lothal Era)
        c. 3000 – 500 BCE : Bharata Settlement at Hastinapura (draft) : The Three Custodians’ Embankment Repair (draft) : Eastern Hillside Seed Exchange (draft) : The Final Voyage of the Kelpfang : Compact of the Furnace Houses (draft) : The Storm-Bone Khan's Warning at Lothal : The Wandering of the Narmada Seed-Mind : Common Spring Access Marked in Stone (draft) : Hearing at the Landslip (draft) : Winter Passage Agreement (draft) : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : The Awakening of the Mask of Vaṛkesh : Birth of Sarita Silversong : Nilgiri Shared Pasture Agreement (draft) : Upland Watershed Quarry Pact (draft) : A Village Preserves Two Seasonal Reckonings (draft) : Yadu Foundation of North Dwarka (draft)
    section The Age of Machinery
        ~1920s equivalent : Agasthya’s Southern Exchange with the Yakshas (draft) : The Antarctic Ice Wall Expedition : Lothal’s Factory Drainage Dispute (draft) : The Cartographic & Mercantile Accord : Chandraketugarh Garudasaur Blood Feud : The Delta Outrigger Skirmishes : Drilling Halted at the Dwarka Gate : The Frontier Marrow Wars : The Great Coal & Dolmen War : The Great Marrow & Coal War : The Day the Ground Broke at the Great Junction : The Mappa Mundi Colonial Insurgencies : The Mappa Mundi Telegraph Sabotage : The Moriah Spore-Blight : Narmada Archives Rival Grove Concession Copies (draft) : Narmada Compares Shadow Tables with Telegraph Time (draft) : The Narmada Upriver Expedition : The Gondwana Spacetime Teleportation : The Battered Ekranoplan's Ice Wall Voyage : Nilgiri Freight Route Hearing (draft) : The Paratethyan Lock Blockades : Polar Voyagers Arrive at Tamralinga : Dispute over Patent Claims on Charcoal Measures (draft) : Rail Succession Wars (draft) : The Saraswati Canal Drains : Tide-Lock Three Opens : The Undersea Lava River and the Red Fog
    section Post-Cataclysmic Era (The Great Shattering)
        after the Collapse : The Golden Season on the Wetlands : The Night of Red Teeth : The Ark Meets Ananya : The Solarpunk Odyssey of the Ark : The Last Puja
```

## The events, by cause

Edges are `successors`. Events sit in the epoch they declare; an event with no edges is not adrift, it simply has no recorded cause or consequence yet.

```mermaid
graph TD
    subgraph epoch_prehistoric["Prehistoric Foundations & Age of Vanaras"]
        E0["The Curse of the Hollow Trees"]
        E1["The Turning of Kunti Against the Seedbearer"]
        E2["The Planting of the Moon-Seed"]
        E3["The Establishment of the Womb Rites"]
        E4["The First Move of the Chess of Fate"]
        E5["The Fang vs. Scale Wars"]
        E6["The Domestication of the Fang Vanguard"]
        E7["The Asura Gondwana Intervention"]
    end
    subgraph epoch_deep_antiquity["Deep Antiquity"]
        E8["The Battle of Mohenjodaro"]
        E9["Forging of the Dragon’s Spine (sample)"]
        E10["The Great Devolvement"]
        E11["Shadow Pact of Saraswati"]
        E12["The Primordial Union under the Asura Planet"]
    end
    subgraph epoch_migrations["Era of Human Migrations"]
        E13["Aravali Massacre & Sanctuary"]
        E14["Battle of Ten Kings (draft)"]
        E15["The Botai Cattle Raid"]
        E16["Dispute over Inherited Household Obligations (draft)"]
        E17["The Jharwa First-Wave & The Shell Pact"]
        E18["Opening of the Naraka Lok Portal"]
        E19["The Narmada Apothecary Herb Quest"]
        E20["The Retreat of Owlman"]
        E21["Sarishne Encounters Manjalaya at a Gate Disturbance (draft)"]
        E22["River Passage of the Bharata Force (draft)"]
        E23["Victory Recitals at the Bharata Court (draft)"]
        E24["Viśvāmitra Lays Down His Seat (draft)"]
        E25["Wiznu and Aryaman Appeal to the Thunder-Bearer (draft)"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E26["Bharata Settlement at Hastinapura (draft)"]
        E27["The Three Custodians’ Embankment Repair (draft)"]
        E28["Eastern Hillside Seed Exchange (draft)"]
        E29["The Final Voyage of the Kelpfang"]
        E30["Compact of the Furnace Houses (draft)"]
        E31["The Storm-Bone Khan's Warning at Lothal"]
        E32["The Wandering of the Narmada Seed-Mind"]
        E33["Common Spring Access Marked in Stone (draft)"]
        E34["Hearing at the Landslip (draft)"]
        E35["Winter Passage Agreement (draft)"]
        E36["Silvershore War"]
        E37["Founding of Lothal"]
        E38["Black Lotus Siege"]
        E39["The Stone Pact"]
        E40["Tendua Crisis and Assassination of Kavik"]
        E41["Retrieval of the Mask of Harappa"]
        E42["Exile of Shaashak and Khadi"]
        E43["The Awakening of the Mask of Vaṛkesh"]
        E44["Birth of Sarita Silversong"]
        E45["Nilgiri Shared Pasture Agreement (draft)"]
        E46["Upland Watershed Quarry Pact (draft)"]
        E47["A Village Preserves Two Seasonal Reckonings (draft)"]
        E48["Yadu Foundation of North Dwarka (draft)"]
    end
    subgraph epoch_current["The Age of Machinery"]
        E49["Agasthya’s Southern Exchange with the Yakshas (draft)"]
        E50["The Antarctic Ice Wall Expedition"]
        E51["Lothal’s Factory Drainage Dispute (draft)"]
        E52["The Cartographic & Mercantile Accord"]
        E53["Chandraketugarh Garudasaur Blood Feud"]
        E54["The Delta Outrigger Skirmishes"]
        E55["Drilling Halted at the Dwarka Gate"]
        E56["The Frontier Marrow Wars"]
        E57["The Great Coal & Dolmen War"]
        E58["The Great Marrow & Coal War"]
        E59["The Day the Ground Broke at the Great Junction"]
        E60["The Mappa Mundi Colonial Insurgencies"]
        E61["The Mappa Mundi Telegraph Sabotage"]
        E62["The Moriah Spore-Blight"]
        E63["Narmada Archives Rival Grove Concession Copies (draft)"]
        E64["Narmada Compares Shadow Tables with Telegraph Time (draft)"]
        E65["The Narmada Upriver Expedition"]
        E66["The Gondwana Spacetime Teleportation"]
        E67["The Battered Ekranoplan's Ice Wall Voyage"]
        E68["Nilgiri Freight Route Hearing (draft)"]
        E69["The Paratethyan Lock Blockades"]
        E70["Polar Voyagers Arrive at Tamralinga"]
        E71["Dispute over Patent Claims on Charcoal Measures (draft)"]
        E72["Rail Succession Wars (draft)"]
        E73["The Saraswati Canal Drains"]
        E74["Tide-Lock Three Opens"]
        E75["The Undersea Lava River and the Red Fog"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E76["The Golden Season on the Wetlands"]
        E77["The Night of Red Teeth"]
        E78["The Ark Meets Ananya"]
        E79["The Solarpunk Odyssey of the Ark"]
        E80["The Last Puja"]
    end
    E81["Argenthal Settlement (draft)"]
    E82["Eastern Bhṛgu Teaching Reaches the Vedda Guilds (draft)"]
    E83["Dual Coral Crown Treaties (draft)"]
    E84["Federal Harbour Charter (draft)"]
    E85["Formation of the Furnace Confederacy (draft)"]
    E86["Grove and Hill Obligations Enter a Legal Roll (draft)"]
    E87["Jharwa Passage into the Yaksha South (draft)"]
    E88["The Last Attendance of Manjalaya (draft)"]
    E89["Lothal Canal Compact (draft)"]
    E90["Nine-Pass Peace (draft)"]
    E91["Plateau Charter Crisis (draft)"]
    E92["Pragjyotisha Hill Autonomy Charter (draft)"]
    E93["Pragjyotisha Adopts the Twin Reckoning (draft)"]
    E94["Expansion of Sky-Island Survey and Mineral Transport (draft)"]
    E95["Vanga Seed Fleet (draft)"]
    E96["Vijayan High Pasture Treaty (draft)"]
    E97["Vijayan Watershed Compact (draft)"]
    E98["War of the Three Estuaries (draft)"]
    E99["Lothal Guild Settlement (draft)"]
    E0 --> E2
    E1 --> E2
    E2 --> E3
    E4 --> E5
    E5 --> E7
    E5 --> E6
    E6 --> E7
    E7 --> E10
    E8 --> E11
    E10 --> E17
    E13 --> E80
    E14 --> E23
    E15 --> E18
    E17 --> E20
    E18 --> E31
    E18 --> E19
    E19 --> E31
    E31 --> E40
    E31 --> E32
    E33 --> E34
    E36 --> E38
    E36 --> E37
    E37 --> E39
    E37 --> E38
    E38 --> E39
    E39 --> E40
    E40 --> E41
    E40 --> E42
    E41 --> E42
    E42 --> E43
    E42 --> E44
    E50 --> E79
    E57 --> E58
    E59 --> E76
    E65 --> E66
    E66 --> E67
    E67 --> E79
    E76 --> E77
    E77 --> E78
    E98 --> E99
```
