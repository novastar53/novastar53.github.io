#!/usr/bin/env python3
"""
Post-build annotation of blog HTML pages:

1. Post pages: insert a date + reading-time line under the post's <h1>.
2. Post pages: insert prev/next post navigation at the bottom of the article.
3. intro.html: append date + reading time to each landing-page card.

Post order, titles, and dates come from _toc.yml + macOS creation dates —
the same sources generate_sidebar.py and generate_rss.py use.

Idempotent: re-running skips pages that already carry the annotations.

Usage:
    python annotate_posts.py site/_build/html
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

SITE_DIR = Path(__file__).parent / "site"
WORDS_PER_MINUTE = 200


def load_post_dates() -> dict[str, str]:
    """Map post name -> ISO date string (source of truth; CI loses birth times)."""
    dates_file = SITE_DIR / "post_dates.yml"
    if dates_file.exists():
        data = yaml.safe_load(dates_file.read_text()) or {}
        return {k: str(v) for k, v in data.items() if not k.startswith("#")}
    return {}


def post_date(name: str, post_dates: dict[str, str]) -> datetime:
    date = post_dates.get(name)
    if date:
        return datetime.fromisoformat(date)
    ts = (SITE_DIR / f"{name}.ipynb").stat().st_mtime
    return datetime.fromtimestamp(ts)


def load_posts():
    """Return [{name, title, date, minutes}] in toc order (newest first)."""
    toc = yaml.safe_load((SITE_DIR / "_toc.yml").read_text())
    post_dates = load_post_dates()
    posts = []
    for s in toc.get("sections", []):
        if "file" not in s:
            continue
        name = s["file"]
        nb_path = SITE_DIR / f"{name}.ipynb"
        if not nb_path.exists():
            continue
        nb = json.loads(nb_path.read_text(encoding="utf-8"))

        title, words = name, 0
        for cell in nb.get("cells", []):
            src = "".join(cell.get("source", []))
            if cell.get("cell_type") == "markdown":
                words += len(re.findall(r"[A-Za-z0-9']+", src))
                if title == name:
                    m = re.search(r"^#\s+(.+)$", src, re.M)
                    if m:
                        title = m.group(1).strip()

        posts.append({
            "name": name,
            "title": title,
            "date": post_date(name, post_dates).strftime("%b %Y"),
            "minutes": max(1, round(words / WORDS_PER_MINUTE)),
        })
    return posts


def annotate_post_page(html_path: Path, post, prev_post, next_post) -> None:
    text = html_path.read_text(encoding="utf-8")

    # Meta line under the h1: date, reading time, Colab link.
    # Replace-by-regex so re-runs upgrade earlier versions of the line.
    colab = (f'<a class="colab-link" href="https://colab.research.google.com/github/'
             f'novastar53/novastar53.github.io/blob/main/site/{post["name"]}.ipynb"'
             f' target="_blank" rel="noopener">Open in Colab &#8599;</a>')
    meta = f'<div class="post-meta">{post["date"]} &middot; {post["minutes"]} min read &middot; {colab}</div>'
    existing = re.search(r'<div class="post-meta">.*?</div>', text, re.S)
    if existing:
        text = text[:existing.start()] + meta + text[existing.end():]
    else:
        m = re.search(r"<h1[^>]*>.*?</h1>", text, re.S)
        if m:
            text = text[:m.end()] + meta + text[m.end():]

    if "post-nav" not in text:
        links = ""
        if prev_post:
            links += (f'<a class="post-nav-link post-nav-prev" href="{prev_post["name"]}.html">'
                      f'&larr; {prev_post["title"]}</a>')
        if next_post:
            links += (f'<a class="post-nav-link post-nav-next" href="{next_post["name"]}.html">'
                      f'{next_post["title"]} &rarr;</a>')
        if links:
            nav = f'<div class="post-nav">{links}</div>'
            marker = '<div class="clearer"></div>'
            if marker in text:
                text = text.replace(marker, nav + "\n" + marker, 1)

    html_path.write_text(text, encoding="utf-8")


def annotate_landing(build_dir: Path, posts) -> None:
    intro = build_dir / "intro.html"
    if not intro.exists():
        return
    text = intro.read_text(encoding="utf-8")

    def add_date(m):
        card = m.group(0)
        if "post-date" in card:
            return card
        href = m.group(1)
        post = next((p for p in posts if p["name"] + ".html" == href), None)
        if not post:
            return card
        date_span = f'<span class="post-date">{post["date"]} &middot; {post["minutes"]} min read</span>'
        return card[:-4] + date_span + "</a>"

    text = re.sub(r'<a class="post-card[^"]*" href="([^"]+)">(?:(?!</a>).)*</a>',
                  add_date, text, flags=re.S)
    intro.write_text(text, encoding="utf-8")


def main() -> None:
    build_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE_DIR / "_build/html"
    posts = load_posts()  # newest first

    for i, post in enumerate(posts):
        prev_post = posts[i - 1] if i > 0 else None           # newer post
        next_post = posts[i + 1] if i < len(posts) - 1 else None  # older post
        html_path = build_dir / f'{post["name"]}.html'
        if html_path.exists():
            annotate_post_page(html_path, post, prev_post, next_post)

    annotate_landing(build_dir, posts)
    print(f"annotated {len(posts)} post pages + landing cards")


if __name__ == "__main__":
    main()
