# The Timeline of South of Tethys

<p class="book-nav"><a href="https://lordlebu.github.io/SouthOfTethys/">The Timeline</a> &middot; <strong>Epochs &amp; Events</strong> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/atlas.html">The Atlas</a> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/memory_map.html">The Memory Map</a></p>

_Generated from `database/events/` and `database/timeline/epochs.json` by `utils/generate_timeline_mermaid.py`. Do not edit by hand._

## The epochs

```mermaid
timeline
    title South of Tethys — the epochs
    section Prehistoric Foundations & Age of Vanaras
        500 MYA – 5 MYA : The Curse of the Hollow Trees : The Fang vs. Scale Wars : The Domestication of the Fang Vanguard : The Asura Gondwana Intervention : The Great Devolvement : The Turning of Kunti Against the Seedbearer : The Planting of the Moon-Seed : The Establishment of the Womb Rites
    section Deep Antiquity
        before the migrations : The Battle of Mohenjodaro : Forging of the Dragon’s Spine (sample) : Shadow Pact of Saraswati
    section Era of Human Migrations
        50K – 5K years ago : Aravali Massacre & Sanctuary : The Botai Cattle Raid : The Jharwa First-Wave & The Shell Pact : Opening of the Naraka Lok Portal : The Narmada Apothecary Herb Quest : The Retreat of Owlman : The Primordial Union under the Asura Planet
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
        E1["The Fang vs. Scale Wars"]
        E2["The Domestication of the Fang Vanguard"]
        E3["The Asura Gondwana Intervention"]
        E4["The Great Devolvement"]
        E5["The Turning of Kunti Against the Seedbearer"]
        E6["The Planting of the Moon-Seed"]
        E7["The Establishment of the Womb Rites"]
    end
    subgraph epoch_deep_antiquity["Deep Antiquity"]
        E8["The Battle of Mohenjodaro"]
        E9["Forging of the Dragon’s Spine (sample)"]
        E10["Shadow Pact of Saraswati"]
    end
    subgraph epoch_migrations["Era of Human Migrations"]
        E11["Aravali Massacre & Sanctuary"]
        E12["The Botai Cattle Raid"]
        E13["The Jharwa First-Wave & The Shell Pact"]
        E14["Opening of the Naraka Lok Portal"]
        E15["The Narmada Apothecary Herb Quest"]
        E16["The Retreat of Owlman"]
        E17["The Primordial Union under the Asura Planet"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E18["The Final Voyage of the Kelpfang"]
        E19["The Storm-Bone Khan's Warning at Lothal"]
        E20["The Wandering of the Narmada Seed-Mind"]
        E21["Silvershore War"]
        E22["Founding of Lothal"]
        E23["Black Lotus Siege"]
        E24["The Stone Pact"]
        E25["Tendua Crisis and Assassination of Kavik"]
        E26["Retrieval of the Mask of Harappa"]
        E27["Exile of Shaashak and Khadi"]
        E28["The Awakening of the Mask of Vaṛkesh"]
        E29["Birth of Sarita Silversong"]
    end
    subgraph epoch_current["Current Era (Age of Machinery)"]
        E30["The Antarctic Ice Wall Expedition"]
        E31["The Narmada Upriver Expedition"]
        E32["The Gondwana Spacetime Teleportation"]
        E33["The Battered Ekranoplan's Ice Wall Voyage"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E34["The Solarpunk Odyssey of the Ark"]
    end
    E0 --> E6
    E1 --> E3
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E13
    E5 --> E6
    E6 --> E7
    E8 --> E10
    E12 --> E14
    E13 --> E16
    E14 --> E19
    E14 --> E15
    E15 --> E19
    E19 --> E25
    E19 --> E20
    E21 --> E23
    E21 --> E22
    E22 --> E24
    E22 --> E23
    E23 --> E24
    E24 --> E25
    E25 --> E26
    E25 --> E27
    E26 --> E27
    E27 --> E28
    E27 --> E29
    E31 --> E32
    E32 --> E33
    E33 --> E34
```
