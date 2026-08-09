"""Placeholder species evolution helper.

Reads from database/fauna when available. No-op if empty.
"""

import sys
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the status glyphs below.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
