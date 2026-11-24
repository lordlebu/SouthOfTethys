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
        c. 3000 – 500 BCE : Bharata Settlement at Hastinapura (draft) : The Final Voyage of the Kelpfang : The Storm-Bone Khan's Warning at Lothal : The Wandering of the Narmada Seed-Mind : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : The Awakening of the Mask of Vaṛkesh : Birth of Sarita Silversong : Yadu Foundation of North Dwarka (draft)
    section The Age of Machinery
        ~1920s equivalent : Agasthya’s Southern Exchange with the Yakshas (draft) : The Antarctic Ice Wall Expedition : Lothal’s Factory Drainage Dispute (draft) : The Cartographic & Mercantile Accord : Chandraketugarh Garudasaur Blood Feud : Delta Embankment Repair and Relief Settlement (draft) : The Delta Outrigger Skirmishes : Drilling Halted at the Dwarka Gate : Eastern Seed Reserve Negotiations (draft) : The Frontier Marrow Wars : Compact of the Furnace Houses (draft) : The Great Coal & Dolmen War : The Great Marrow & Coal War : The Day the Ground Broke at the Great Junction : Grove and Hill Obligations Enter a Legal Roll (draft) : Hill Assembly Affirms Common Spring Access (draft) : The Mappa Mundi Colonial Insurgencies : The Mappa Mundi Telegraph Sabotage : The Moriah Spore-Blight : Narmada Archives Rival Grove Concession Copies (draft) : Narmada Compares Shadow Tables with Telegraph Time (draft) : The Narmada Upriver Expedition : The Gondwana Spacetime Teleportation : The Battered Ekranoplan's Ice Wall Voyage : Nilgiri Freight Route Hearing (draft) : The Paratethyan Lock Blockades : Polar Voyagers Arrive at Tamralinga : Dispute over Patent Claims on Charcoal Measures (draft) : Rail Succession Wars (draft) : Highland Hearing at the Landslip (draft) : The Saraswati Canal Drains : Highland Winter Passage Agreement (draft) : Tide-Lock Three Opens : Nilgiri Shared Pasture Agreement (draft) : The Undersea Lava River and the Red Fog : Upland Watershed Quarry Pact (draft) : Debate over a Shared Seasonal Reckoning (draft)
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
        E27["The Final Voyage of the Kelpfang"]
        E28["The Storm-Bone Khan's Warning at Lothal"]
        E29["The Wandering of the Narmada Seed-Mind"]
        E30["Silvershore War"]
        E31["Founding of Lothal"]
        E32["Black Lotus Siege"]
        E33["The Stone Pact"]
        E34["Tendua Crisis and Assassination of Kavik"]
        E35["Retrieval of the Mask of Harappa"]
        E36["Exile of Shaashak and Khadi"]
        E37["The Awakening of the Mask of Vaṛkesh"]
        E38["Birth of Sarita Silversong"]
        E39["Yadu Foundation of North Dwarka (draft)"]
    end
    subgraph epoch_current["The Age of Machinery"]
        E40["Agasthya’s Southern Exchange with the Yakshas (draft)"]
        E41["The Antarctic Ice Wall Expedition"]
        E42["Lothal’s Factory Drainage Dispute (draft)"]
        E43["The Cartographic & Mercantile Accord"]
        E44["Chandraketugarh Garudasaur Blood Feud"]
        E45["Delta Embankment Repair and Relief Settlement (draft)"]
        E46["The Delta Outrigger Skirmishes"]
        E47["Drilling Halted at the Dwarka Gate"]
        E48["Eastern Seed Reserve Negotiations (draft)"]
        E49["The Frontier Marrow Wars"]
        E50["Compact of the Furnace Houses (draft)"]
        E51["The Great Coal & Dolmen War"]
        E52["The Great Marrow & Coal War"]
        E53["The Day the Ground Broke at the Great Junction"]
        E54["Grove and Hill Obligations Enter a Legal Roll (draft)"]
        E55["Hill Assembly Affirms Common Spring Access (draft)"]
        E56["The Mappa Mundi Colonial Insurgencies"]
        E57["The Mappa Mundi Telegraph Sabotage"]
        E58["The Moriah Spore-Blight"]
        E59["Narmada Archives Rival Grove Concession Copies (draft)"]
        E60["Narmada Compares Shadow Tables with Telegraph Time (draft)"]
        E61["The Narmada Upriver Expedition"]
        E62["The Gondwana Spacetime Teleportation"]
        E63["The Battered Ekranoplan's Ice Wall Voyage"]
        E64["Nilgiri Freight Route Hearing (draft)"]
        E65["The Paratethyan Lock Blockades"]
        E66["Polar Voyagers Arrive at Tamralinga"]
        E67["Dispute over Patent Claims on Charcoal Measures (draft)"]
        E68["Rail Succession Wars (draft)"]
        E69["Highland Hearing at the Landslip (draft)"]
        E70["The Saraswati Canal Drains"]
        E71["Highland Winter Passage Agreement (draft)"]
        E72["Tide-Lock Three Opens"]
        E73["Nilgiri Shared Pasture Agreement (draft)"]
        E74["The Undersea Lava River and the Red Fog"]
        E75["Upland Watershed Quarry Pact (draft)"]
        E76["Debate over a Shared Seasonal Reckoning (draft)"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E77["The Golden Season on the Wetlands"]
        E78["The Night of Red Teeth"]
        E79["The Ark Meets Ananya"]
        E80["The Solarpunk Odyssey of the Ark"]
        E81["The Last Puja"]
    end
    E82["Argenthal Settlement (draft)"]
    E83["Eastern Bhṛgu Teaching Reaches the Vedda Guilds (draft)"]
    E84["Dual Coral Crown Treaties (draft)"]
    E85["Federal Harbour Charter (draft)"]
    E86["Formation of the Furnace Confederacy (draft)"]
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
    E13 --> E81
    E14 --> E23
    E15 --> E18
    E17 --> E20
    E18 --> E28
    E18 --> E19
    E19 --> E28
    E28 --> E34
    E28 --> E29
    E30 --> E32
    E30 --> E31
    E31 --> E33
    E31 --> E32
    E32 --> E33
    E33 --> E34
    E34 --> E35
    E34 --> E36
    E35 --> E36
    E36 --> E37
    E36 --> E38
    E41 --> E80
    E51 --> E52
    E53 --> E77
    E55 --> E69
    E61 --> E62
    E62 --> E63
    E63 --> E80
    E77 --> E78
    E78 --> E79
    E98 --> E99
```
