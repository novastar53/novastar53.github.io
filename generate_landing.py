#!/usr/bin/env python3
"""
Generate the landing-page cards in site/index.md from _toc.yml.

The featured card (with teaser) is the newest post in _toc.yml; the
"Recent posts" grid shows the next five. Per-post thumbnails, topic tags,
and teaser overrides live in site/post_meta.yml; when omitted, the
thumbnail falls back to the first markdown image in the notebook and the
teaser to its opening paragraph.

Run automatically by `make build` before jupyter-book. Idempotent.

Usage:
    python generate_landing.py
"""

import json
import re
from pathlib import Path

import yaml

SITE_DIR = Path(__file__).parent / "site"
INDEX = SITE_DIR / "index.md"
TOC = SITE_DIR / "_toc.yml"
META = SITE_DIR / "post_meta.yml"

GRID_SIZE = 5
TEASER_MAX = 260

FEATURED_BEGIN = "<!-- BEGIN GENERATED CARDS -->"
FEATURED_END = "<!-- END GENERATED CARDS -->"
GRID_BEGIN = "<!-- BEGIN GENERATED GRID -->"
GRID_END = "<!-- END GENERATED GRID -->"


def load_meta() -> dict:
    if META.exists():
        data = yaml.safe_load(META.read_text()) or {}
        return {k: v for k, v in data.items() if not k.startswith("#")}
    return {}


def first_markdown_image(nb: dict) -> str | None:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", "".join(cell.get("source", [])))
        if m:
            return m.group(1)
    return None


def title_and_teaser(nb: dict, name: str) -> tuple[str, str | None]:
    """First # heading, and the first paragraph of prose after it."""
    title, teaser = name, None
    seen_title = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = "".join(cell.get("source", []))
        if title == name:
            m = re.search(r"^#\s+(.+)$", text, re.M)
            if not m:
                continue
            title = m.group(1).strip()
            seen_title = True
            text = text[m.end():]
        if not seen_title or teaser:
            continue
        # skip headings and images, take the first real paragraph
        for para in re.split(r"\n\s*\n", text):
            para = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", para)
            para = re.sub(r"^#+.*$", "", para, flags=re.M).strip()
            if para:
                teaser = para
                break
    return title, teaser


def flatten_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)   # links -> text
    text = re.sub(r"<[^>]+>", "", text)                     # html tags
    text = re.sub(r"[*_`]+", "", text)                       # emphasis/code
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate(text: str) -> str:
    if len(text) <= TEASER_MAX:
        return text
    cut = text[:TEASER_MAX]
    m = re.search(r"[.!?](?:\s|$)", cut[150:])
    if m:
        return cut[:150 + m.start() + 1]
    return cut.rsplit(" ", 1)[0] + "…"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def img_src(image: str | None) -> str | None:
    if not image:
        return None
    if image.startswith(("http", "_static/")):
        return image
    return f"_images/{Path(image).name}"


def load_posts():
    toc = yaml.safe_load(TOC.read_text())
    meta = load_meta()
    posts = []
    for s in toc.get("sections", []):
        if "file" not in s:
            continue
        name = s["file"]
        nb_path = SITE_DIR / f"{name}.ipynb"
        if not nb_path.exists():
            continue
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        title, teaser = title_and_teaser(nb, name)
        post_meta = meta.get(name, {})
        posts.append({
            "name": name,
            "title": title,
            "tag": post_meta.get("tag"),
            "image": img_src(post_meta.get("image") or first_markdown_image(nb)),
            "teaser": post_meta.get("teaser") or (truncate(flatten_md(teaser)) if teaser else None),
        })
    return posts


def featured_card(post: dict) -> str:
    parts = [f'<a class="post-card post-card-featured" href="{post["name"]}.html">']
    if post["image"]:
        parts.append(f'  <img class="post-thumb" src="{post["image"]}" alt="" loading="lazy">')
    parts.append('  <span class="featured-text">')
    if post["tag"]:
        parts.append(f'    <span class="post-tag">Latest &middot; {esc(post["tag"])}</span>')
    parts.append(f'    <span class="post-title">{esc(post["title"])}</span>')
    if post["teaser"]:
        parts.append(f'    <span class="post-teaser">{esc(post["teaser"])}</span>')
    parts.append('  </span>')
    parts.append('</a>')
    return "\n".join(parts)


def grid_card(post: dict) -> str:
    parts = [f'  <a class="post-card" href="{post["name"]}.html">']
    if post["image"]:
        parts.append(f'    <img class="post-thumb" src="{post["image"]}" alt="" loading="lazy">')
    if post["tag"]:
        parts.append(f'    <span class="post-tag">{esc(post["tag"])}</span>')
    parts.append(f'    <span class="post-title">{esc(post["title"])}</span>')
    parts.append('  </a>')
    return "\n".join(parts)


def replace_block(text: str, begin: str, end: str, content: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"markers {begin!r} ... {end!r} not found in {INDEX}")
    return pattern.sub(begin + "\n" + content + "\n" + end, text)


def main() -> None:
    posts = load_posts()
    if not posts:
        raise SystemExit("no posts found in _toc.yml")
    featured, grid = posts[0], posts[1:1 + GRID_SIZE]

    text = INDEX.read_text(encoding="utf-8")
    text = replace_block(text, FEATURED_BEGIN, FEATURED_END, featured_card(featured))
    text = replace_block(text, GRID_BEGIN, GRID_END, "\n\n".join(grid_card(p) for p in grid))
    INDEX.write_text(text, encoding="utf-8")
    print(f"landing page: featured '{featured['name']}', grid: {', '.join(p['name'] for p in grid)}")


if __name__ == "__main__":
    main()
