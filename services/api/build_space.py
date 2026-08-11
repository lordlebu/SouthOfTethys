"""Assemble a deployable Hugging Face Space from this repo.

A Space is its own git repo and wants two things at its root that this repo cannot give it:
a `Dockerfile`, and a `README.md` whose YAML frontmatter configures the Space. This repo's
README is the lore one and must not be overwritten, so rather than pushing this repository
to a Space, this builds a small directory containing only what the service reads at runtime.

That also keeps the token surface small: the Space contains no `.env`, no notebooks, no
model weights, and none of the tooling -- just the API, the retrieval module it imports,
canon, and the prebuilt index.

    REPO_DIR=. CHROMA_PERSIST_DIR=storage/chroma python services/chroma/index_chroma_service.py
    python services/api/build_space.py

Then push `dist-space/` to the Space's git remote. Secrets are set in the Space UI and never
committed.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Frontmatter is what makes it a Space rather than a plain repo. `app_port` must match the
# port the Dockerfile's CMD binds, or the Space builds and then serves nothing.
README = """---
title: South of Tethys Canon API
emoji: 🌊
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
short_description: Retrieval over the Jambhudweepa canon, for the South of Tethys game
---

# South of Tethys — canon API

Retrieval over the canonical entities of Jambhudweepa, and grounded journal passages written
from what it retrieves. The game at [lordlebu.github.io/4000BCESaraswathy](https://lordlebu.github.io/4000BCESaraswathy/)
calls this to ask what canon knows about the tile the player is standing on.

| endpoint | cost | access |
|---|---|---|
| `GET /health` | none | public |
| `POST /lore` | none — local retrieval | public |
| `POST /ask` | inference provider | requires `X-Canon-Key` |

`/ask` is gated because it spends the owner's inference quota per call, and CORS does not
prevent that — it is a browser policy and command-line clients ignore it. With generation
configured and no key set the endpoint refuses rather than serving an open billable route.

The index is baked into the image, so canon changes reach this Space only through a rebuild.

Built from [lordlebu/SouthOfTethys](https://github.com/lordlebu/SouthOfTethys) —
`python services/api/build_space.py`.
"""

# Only what main.py touches at runtime.
COPY = [
    ("services/api/main.py", "services/api/main.py"),
    ("services/api/requirements.txt", "services/api/requirements.txt"),
    ("services/api/Dockerfile", "Dockerfile"),
    ("vidur_portal/snippet_processor.py", "vidur_portal/snippet_processor.py"),
    ("database", "database"),
    ("storage/chroma", "storage/chroma"),
]

# Belt and braces: never let a secret into the assembled directory, whatever else changes.
NEVER = {".env", ".env.local", ".env.production", "hf_token.txt", "secrets.json"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=REPO / "dist-space")
    args = ap.parse_args()

    index = REPO / "storage" / "chroma"
    if not index.exists() or not any(index.iterdir()):
        print("ERROR: storage/chroma is empty. Build the index first:")
        print("  REPO_DIR=. CHROMA_PERSIST_DIR=storage/chroma python services/chroma/index_chroma_service.py")
        return 1

    out = args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for src_rel, dst_rel in COPY:
        src, dst = REPO / src_rel, out / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *NEVER))
        else:
            shutil.copy2(src, dst)

    (out / "README.md").write_text(README, encoding="utf-8", newline="\n")
    # The Space builds from its own root, so nothing above it is available.
    (out / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\n.env.*\n", encoding="utf-8", newline="\n")

    leaked = [p for p in out.rglob("*") if p.name in NEVER]
    if leaked:
        print("ERROR: refusing to leave secrets in the build:", [str(p) for p in leaked])
        return 1

    files = [p for p in out.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files) / 1048576
    chunks = "unknown"
    try:
        import chromadb

        chunks = chromadb.PersistentClient(path=str(out / "storage" / "chroma")).get_collection(
            "southoftethys"
        ).count()
    except Exception:
        pass

    print(f"assembled {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    print(f"  {len(files)} files, {size:.1f} MB, {chunks} indexed chunks")
    print()
    print("push it:")
    print(f"  cd {out}")
    print("  git init && git add -A && git commit -m 'Canon API'")
    print("  git remote add space https://huggingface.co/spaces/<you>/<space>")
    print("  git push space main --force")
    print()
    print("then in the Space settings — Secrets: HF_TOKEN, CANON_API_KEY;")
    print("Variables: CANON_LLM, CANON_ALLOWED_ORIGINS=https://lordlebu.github.io")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
