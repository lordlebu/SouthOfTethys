# The Timeline of South of Tethys

_Generated from `database/events/` and `database/timeline/epochs.json` by `utils/generate_timeline_mermaid.py`. Do not edit by hand._

## The epochs

```mermaid
timeline
    title South of Tethys — the epochs
    section Prehistoric Foundations & Age of Vanaras
        500 MYA – 5 MYA : (no events recorded yet)
    section Deep Antiquity
        before the migrations : Forging of the Dragon’s Spine : Shadow Pact of Saraswati
    section Era of Human Migrations
        50K – 5K years ago : Aravali Massacre & Sanctuary : Opening of the Naraka Lok Portal
    section Civilization Dawn (Lothal Era)
        c. 3000 – 500 BCE : Silvershore War : Founding of Lothal : Black Lotus Siege : The Stone Pact : Tendua Crisis and Assassination of Kavik : Retrieval of the Mask of Harappa : Exile of Shaashak and Khadi : Birth of Sarita Silversong
    section Current Era (Age of Machinery)
        ~1920s equivalent : (no events recorded yet)
    section Post-Cataclysmic Era (The Great Shattering)
        after the Collapse : (no events recorded yet)
```

## The events, by cause

Edges are `successors`. Events sit in the epoch they declare; an event with no edges is not adrift, it simply has no recorded cause or consequence yet.

```mermaid
graph TD
    subgraph epoch_deep_antiquity["Deep Antiquity"]
        E0["Forging of the Dragon’s Spine"]
        E1["Shadow Pact of Saraswati"]
    end
    subgraph epoch_migrations["Era of Human Migrations"]
        E2["Aravali Massacre & Sanctuary"]
        E3["Opening of the Naraka Lok Portal"]
    end
    subgraph epoch_civilization_dawn["Civilization Dawn (Lothal Era)"]
        E4["Silvershore War"]
        E5["Founding of Lothal"]
        E6["Black Lotus Siege"]
        E7["The Stone Pact"]
        E8["Tendua Crisis and Assassination of Kavik"]
        E9["Retrieval of the Mask of Harappa"]
        E10["Exile of Shaashak and Khadi"]
        E11["Birth of Sarita Silversong"]
    end
    E4 --> E6
    E4 --> E5
    E5 --> E7
    E5 --> E6
    E6 --> E7
    E7 --> E8
    E8 --> E9
    E8 --> E10
    E9 --> E10
    E10 --> E11
```

## Epochs with no events yet

- **Prehistoric Foundations & Age of Vanaras** — 500 MYA – 5 MYA
- **Current Era (Age of Machinery)** — ~1920s equivalent
- **Post-Cataclysmic Era (The Great Shattering)** — after the Collapse
