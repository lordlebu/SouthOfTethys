"""Placeholder species evolution helper.

Reads from database/fauna when available. No-op if empty.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FAUNA_DIR = BASE / "database" / "fauna"


def main():
    if not FAUNA_DIR.exists():
        print("⚠️  No database/fauna directory; skipping evolution step.")
        return
    files = list(FAUNA_DIR.glob("*.json"))
    print(f"✅ Found {len(files)} fauna entities under database/fauna (no mutation applied).")


if __name__ == "__main__":
    main()
