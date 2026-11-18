#!/usr/bin/env python3
"""
Generate an RSS 2.0 feed for the blog and inject <link rel="alternate">
autodiscovery tags into every built HTML page.

Post metadata comes from the same sources as the sidebar:
- Order and membership: site/_toc.yml (published posts, newest first)
- Dates: macOS file creation time (st_birthtime), same as generate_sidebar.py

Usage:
    python generate_rss.py site/_build/html https://blog.vikrampawar.com
"""

import json
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

import yaml

SITE_DIR = Path(__file__).parent / "site"


def load_post_dates() -> dict[str, str]:
    """Map post name -> ISO date string (source of truth; CI loses birth times)."""
    dates_file = SITE_DIR / "post_dates.yml"
    if dates_file.exists():
        data = yaml.safe_load(dates_file.read_text()) or {}
        return {k: str(v) for k, v in data.items() if not k.startswith("#")}
    return {}


def file_creation_date(name: str, post_dates: dict[str, str]) -> datetime:
    """Publication date for a post, preferring post_dates.yml."""
    date = post_dates.get(name)
    if date:
        return datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    ts = (SITE_DIR / f"{name}.ipynb").stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def notebook_title(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown":
            m = re.search(r"^#\s+(.+)$", "".join(cell.get("source", [])), re.M)
            if m:
                return m.group(1).strip()
    return nb_path.stem


def notebook_teaser(nb_path: Path) -> str:
    """First paragraph of prose, markdown-stripped, as the feed summary."""
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = "".join(cell.get("source", []))
        m = re.search(r"^#\s+.+$", text, re.M)
        if m:
            text = text[m.end():]
        # drop image and raw-HTML lines so the teaser is prose
        text = "\n".join(
            l for l in text.split("\n")
            if not l.lstrip().startswith(("!", "<"))
        )
        m = re.search(r"^([^#\n].+(?:\n(?!\s*#)[^\n]*)*)", text.strip())
        if m:
            plain = m.group(1)
            plain = re.sub(r"\$\$.+?\$\$", "", plain, flags=re.S)  # display math
            plain = re.sub(r"\$[^$\n]+\$", "", plain)               # inline math
            plain = re.sub(r"[*_`>\[\]()#]", "", plain).strip()
            plain = re.sub(r"\s+", " ", plain)
            if plain:
                return plain[:500]
    return ""


def main() -> None:
    build_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE_DIR / "_build/html"
    base_url = sys.argv[2] if len(sys.argv) > 2 else "https://blog.vikrampawar.com"
    base_url = base_url.rstrip("/")

    toc = yaml.safe_load((SITE_DIR / "_toc.yml").read_text())
    posts = [s["file"] for s in toc.get("sections", []) if "file" in s]
    post_dates = load_post_dates()

    items = []
    for name in posts:
        nb_path = SITE_DIR / f"{name}.ipynb"
        if not nb_path.exists():
            continue
        date = file_creation_date(name, post_dates)
        title = notebook_title(nb_path)
        teaser = notebook_teaser(nb_path)
        link = f"{base_url}/{name}.html"
        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{format_datetime(date)}</pubDate>
      <description>{escape(teaser)}</description>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Vikram's Data Science Blog</title>
    <link>{base_url}/</link>
    <description>A blog exploring AI and Machine Learning</description>
    <language>en-us</language>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (build_dir / "feed.xml").write_text(feed, encoding="utf-8")

    # Feed autodiscovery in every page's <head>
    alternate = f'<link rel="alternate" type="application/rss+xml" title="RSS feed" href="{base_url}/feed.xml" />'
    for html_file in build_dir.glob("*.html"):
        text = html_file.read_text(encoding="utf-8")
        if 'rel="alternate"' in text:
            continue
        if "<head>" in text:
            text = text.replace("<head>", f"<head>\n    {alternate}", 1)
            html_file.write_text(text, encoding="utf-8")

    print(f"feed.xml written with {len(items)} items; autodiscovery added to HTML pages")


if __name__ == "__main__":
    main()
