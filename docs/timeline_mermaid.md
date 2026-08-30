# The Timeline of South of Tethys

<p class="book-nav"><a href="https://lordlebu.github.io/SouthOfTethys/">The Timeline</a> &middot; <strong>Epochs &amp; Events</strong> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/atlas.html">The Atlas</a> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/memory_map.html">The Memory Map</a></p>

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
        50K – 5K years ago : Aravali Massacre & Sanctuary : The Botai Cattle Raid : The Jharwa First-Wave & The Shell Pact : Opening of the Naraka Lok Portal : The Narmada Apothecary Herb Quest : The Retreat of Owlman
    section Civilization Dawn (Lothal Era)
        c. 3000 – 500 BCE : The Final Voyage of the Kelpfang : The Storm-Bone Khan's Warning at Lothal : The Wandering of the Narmada Seed-Mind : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : The Awakening of the Mask of Vaṛkesh : Birth of Sarita Silversong
    section Current Era (Age of Machinery)
        ~1920s equivalent : The Antarctic Ice Wall Expedition : The Narmada Upriver Expedition : The Gondwana Spacetime Teleportation : The Battered Ekranoplan's Ice Wall Voyage
    section Post-Cataclysmic Era (The Great Shattering)
        after the Collapse : The Solarpunk Odyssey of the Ark
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
        E14["The Botai Cattle Raid"]
        E15["The Jharwa First-Wave & The Shell Pact"]
        E16["Opening of the Naraka Lok Portal"]
        E17["The Narmada Apothecary Herb Quest"]
        E18["The Retreat of Owlman"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E19["The Final Voyage of the Kelpfang"]
        E20["The Storm-Bone Khan's Warning at Lothal"]
        E21["The Wandering of the Narmada Seed-Mind"]
        E22["Silvershore War"]
        E23["Founding of Lothal"]
        E24["Black Lotus Siege"]
        E25["The Stone Pact"]
        E26["Tendua Crisis and Assassination of Kavik"]
        E27["Retrieval of the Mask of Harappa"]
        E28["Exile of Shaashak and Khadi"]
        E29["The Awakening of the Mask of Vaṛkesh"]
        E30["Birth of Sarita Silversong"]
    end
    subgraph epoch_current["Current Era (Age of Machinery)"]
        E31["The Antarctic Ice Wall Expedition"]
        E32["The Narmada Upriver Expedition"]
        E33["The Gondwana Spacetime Teleportation"]
        E34["The Battered Ekranoplan's Ice Wall Voyage"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E35["The Solarpunk Odyssey of the Ark"]
    end
    E0 --> E2
    E1 --> E2
    E2 --> E3
    E4 --> E5
    E5 --> E7
    E5 --> E6
    E6 --> E7
    E7 --> E10
    E8 --> E11
    E10 --> E15
    E14 --> E16
    E15 --> E18
    E16 --> E20
    E16 --> E17
    E17 --> E20
    E20 --> E26
    E20 --> E21
    E22 --> E24
    E22 --> E23
    E23 --> E25
    E23 --> E24
    E24 --> E25
    E25 --> E26
    E26 --> E27
    E26 --> E28
    E27 --> E28
    E28 --> E29
    E28 --> E30
    E31 --> E35
    E32 --> E33
    E33 --> E34
    E34 --> E35
```
