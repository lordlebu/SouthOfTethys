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
    ("memory_map.md", "memory_map.html", "The Memory Map"),
    ("bestiary.md", "bestiary.html", "The Bestiary"),
    ("apothecary.md", "apothecary.html", "The Apothecary"),
    ("workshop.md", "workshop.html", "The Workshop"),
    ("cookbook.md", "cookbook.html", "The Cookbook"),
]


def nav(current: str) -> str:
    """A nav bar for a generated page, with the current one not linked.

    Emitted as raw HTML rather than markdown so the stylesheet has something to hook. A
    markdown line can only be reached as `section > h1 + p`, which is every page's opening
    paragraph -- it would have set `decisions.md` and both READMEs in monospace small caps too.

    kramdown passes an HTML block through untouched, so the class survives to GitHub Pages.
    github.com strips the class but keeps the paragraph and the links, where there is no
    stylesheet anyway and it reads fine as a line of prose.
    """
    parts = []
    for filename, page, label in PAGES:
        # "Epochs & Events" carries an ampersand, and this is HTML now rather than markdown.
        safe = label.replace("&", "&amp;")
        if filename == current:
            parts.append(f"<strong>{safe}</strong>")
        else:
            parts.append(f'<a href="{SITE}/{page}">{safe}</a>')
    return '<p class="book-nav">' + " &middot; ".join(parts) + "</p>"
