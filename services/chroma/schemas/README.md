This folder contains JSON Schema definitions for Chroma vector collections used by the SouthOfTethys indexing service.

Files:
- `events.schema.json` — schema for event-derived vectors (timeline entries).
- `characters.schema.json` — schema for character profile vectors.
- `snippets.schema.json` — schema for free-form text snippets.
- `documents.schema.json` — schema for general documents (manuals, large text files).

Usage:
1. Use the `validate_metadata.py` helper to validate the `metadata` payload before inserting vectors.
2. Keep the schemas in sync with any extractor changes. Add fields as optional to maintain backwards compatibility.

Security:
- Do not commit real PII into the repository. Store sensitive metadata externally if required.
