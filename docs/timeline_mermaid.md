# The Timeline of South of Tethys

[The Timeline](https://lordlebu.github.io/SouthOfTethys/) · **Epochs & Events** · [The Atlas](https://lordlebu.github.io/SouthOfTethys/atlas.html)

_Generated from `database/events/` and `database/timeline/epochs.json` by `utils/generate_timeline_mermaid.py`. Do not edit by hand._

## The epochs

```mermaid
timeline
    title South of Tethys — the epochs
    section Prehistoric Foundations & Age of Vanaras
        500 MYA – 5 MYA : The Fang vs. Scale Wars : The Asura Gondwana Intervention : The Great Devolvement
    section Deep Antiquity
        before the migrations : Forging of the Dragon’s Spine (sample) : Shadow Pact of Saraswati
    section Era of Human Migrations
        50K – 5K years ago : Aravali Massacre & Sanctuary : The Botai Cattle Raid : The Jharwa First-Wave & The Shell Pact : Opening of the Naraka Lok Portal : The Retreat of Owlman
    section Civilization Dawn (Lothal Era)
        c. 3000 – 500 BCE : The Final Voyage of the Kelpfang : The Storm-Bone Khan's Warning at Lothal : The Wandering of the Narmada Seed-Mind : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : Birth of Sarita Silversong
    section Current Era (Age of Machinery)
        ~1920s equivalent : The Antarctic Ice Wall Expedition
    section Post-Cataclysmic Era (The Great Shattering)
        after the Collapse : The Solarpunk Odyssey of the Ark
```

## The events, by cause

Edges are `successors`. Events sit in the epoch they declare; an event with no edges is not adrift, it simply has no recorded cause or consequence yet.

```mermaid
graph TD
    subgraph epoch_prehistoric["Prehistoric Foundations & Age of Vanaras"]
        E0["The Fang vs. Scale Wars"]
        E1["The Asura Gondwana Intervention"]
        E2["The Great Devolvement"]
    end
    subgraph epoch_deep_antiquity["Deep Antiquity"]
        E3["Forging of the Dragon’s Spine (sample)"]
        E4["Shadow Pact of Saraswati"]
    end
    subgraph epoch_migrations["Era of Human Migrations"]
        E5["Aravali Massacre & Sanctuary"]
        E6["The Botai Cattle Raid"]
        E7["The Jharwa First-Wave & The Shell Pact"]
        E8["Opening of the Naraka Lok Portal"]
        E9["The Retreat of Owlman"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E10["The Final Voyage of the Kelpfang"]
        E11["The Storm-Bone Khan's Warning at Lothal"]
        E12["The Wandering of the Narmada Seed-Mind"]
        E13["Silvershore War"]
        E14["Founding of Lothal"]
        E15["Black Lotus Siege"]
        E16["The Stone Pact"]
        E17["Tendua Crisis and Assassination of Kavik"]
        E18["Retrieval of the Mask of Harappa"]
        E19["Exile of Shaashak and Khadi"]
        E20["Birth of Sarita Silversong"]
    end
    subgraph epoch_current["Current Era (Age of Machinery)"]
        E21["The Antarctic Ice Wall Expedition"]
    end
    subgraph epoch_post_cataclysm["Post-Cataclysmic Era (The Great Shattering)"]
        E22["The Solarpunk Odyssey of the Ark"]
    end
    E0 --> E1
    E1 --> E2
    E2 --> E7
    E6 --> E8
    E7 --> E9
    E8 --> E11
    E11 --> E17
    E11 --> E12
    E13 --> E15
    E13 --> E14
    E14 --> E16
    E14 --> E15
    E15 --> E16
    E16 --> E17
    E17 --> E18
    E17 --> E19
    E18 --> E19
    E19 --> E20
```
