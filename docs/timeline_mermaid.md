# The Timeline of South of Tethys

<p class="book-nav"><a href="https://lordlebu.github.io/SouthOfTethys/">The Timeline</a> &middot; <strong>Epochs &amp; Events</strong> &middot; <a href="https://lordlebu.github.io/SouthOfTethys/atlas.html">The Atlas</a></p>

_Generated from `database/events/` and `database/timeline/epochs.json` by `utils/generate_timeline_mermaid.py`. Do not edit by hand._

## The epochs

```mermaid
timeline
    title South of Tethys — the epochs
    section Prehistoric Foundations & Age of Vanaras
        500 MYA – 5 MYA : The Curse of the Hollow Trees : The Fang vs. Scale Wars : The Asura Gondwana Intervention : The Great Devolvement : The Planting of the Moon-Seed : The Establishment of the Womb Rites
    section Deep Antiquity
        before the migrations : Forging of the Dragon’s Spine (sample) : Shadow Pact of Saraswati
    section Era of Human Migrations
        50K – 5K years ago : Aravali Massacre & Sanctuary : The Botai Cattle Raid : The Jharwa First-Wave & The Shell Pact : Opening of the Naraka Lok Portal : The Retreat of Owlman : The Primordial Union under the Asura Planet
    section Civilization Dawn (Lothal Era)
        c. 3000 – 500 BCE : The Final Voyage of the Kelpfang : The Storm-Bone Khan's Warning at Lothal : The Wandering of the Narmada Seed-Mind : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : Birth of Sarita Silversong
    section Current Era (Age of Machinery)
        ~1920s equivalent : The Antarctic Ice Wall Expedition : The Narmada Upriver Expedition : The Gondwana Spacetime Teleportation
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
        E2["The Asura Gondwana Intervention"]
        E3["The Great Devolvement"]
        E4["The Planting of the Moon-Seed"]
        E5["The Establishment of the Womb Rites"]
    end
    subgraph epoch_deep_antiquity["Deep Antiquity"]
        E6["Forging of the Dragon’s Spine (sample)"]
        E7["Shadow Pact of Saraswati"]
    end
    subgraph epoch_migrations["Era of Human Migrations"]
        E8["Aravali Massacre & Sanctuary"]
        E9["The Botai Cattle Raid"]
        E10["The Jharwa First-Wave & The Shell Pact"]
        E11["Opening of the Naraka Lok Portal"]
        E12["The Retreat of Owlman"]
        E13["The Primordial Union under the Asura Planet"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E14["The Final Voyage of the Kelpfang"]
        E15["The Storm-Bone Khan's Warning at Lothal"]
        E16["The Wandering of the Narmada Seed-Mind"]
        E17["Silvershore War"]
        E18["Founding of Lothal"]
        E19["Black Lotus Siege"]
        E20["The Stone Pact"]
        E21["Tendua Crisis and Assassination of Kavik"]
        E22["Retrieval of the Mask of Harappa"]
        E23["Exile of Shaashak and Khadi"]
        E24["Birth of Sarita Silversong"]
    end
    subgraph epoch_current["Current Era (Age of Machinery)"]
        E25["The Antarctic Ice Wall Expedition"]
        E26["The Narmada Upriver Expedition"]
        E27["The Gondwana Spacetime Teleportation"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E28["The Solarpunk Odyssey of the Ark"]
    end
    E0 --> E4
    E1 --> E2
    E2 --> E3
    E3 --> E10
    E4 --> E5
    E9 --> E11
    E10 --> E12
    E11 --> E15
    E15 --> E21
    E15 --> E16
    E17 --> E19
    E17 --> E18
    E18 --> E20
    E18 --> E19
    E19 --> E20
    E20 --> E21
    E21 --> E22
    E21 --> E23
    E22 --> E23
    E23 --> E24
    E26 --> E27
```
