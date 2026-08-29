"""The published book's pages, and the nav that links them.

`docs/_config.yml` carried a `header_pages` list naming all three. It did nothing:
`header_pages` is a **minima** feature, and this site uses `pages-themes/minimal`, whose
sidebar renders the title, the description and a link to the repository and stops. The atlas
and the timeline were published, reachable, and linked from nowhere -- you had to know the URL.

That is the same failure the Mermaid include had: from inside the repository it looked done,
because the config was there and the workflow was green. Only fetching the built page and
counting anchors shows it.

Absolute URLs, deliberately. These pages have two render targets -- the Pages site, where
Jekyll turns `atlas.md` into `atlas.html`, and github.com, which renders the markdown directly.
A relative `atlas.html` 404s in the repository and a relative `atlas.md` 404s on the site. The
published URL is the one address that resolves from both.
"""

SITE = "https://lordlebu.github.io/SouthOfTethys"

# filename -> (published page, label)
PAGES = [
    ("index.md", "", "The Timeline"),
    ("timeline_mermaid.md", "timeline_mermaid.html", "Epochs & Events"),
    ("atlas.md", "atlas.html", "The Atlas"),
]


def nav(current: str) -> str:
    """A one-line nav for a generated page, with the current one not linked."""
    parts = []
    for filename, page, label in PAGES:
        if filename == current:
            parts.append(f"**{label}**")
        else:
            parts.append(f"[{label}]({SITE}/{page})")
    return " · ".join(parts)
