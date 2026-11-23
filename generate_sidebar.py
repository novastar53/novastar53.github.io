#!/usr/bin/env python3
"""Generate sidebar year/month groupings from post dates.

Dates come from site/post_dates.yml (the source of truth, since CI
checkouts lose file-creation times); falls back to file birth time.
Produces a nested mapping {year: {month: [post, ...]}} that
sidebar_template.js renders as a two-level collapsible menu.
"""

import re
from datetime import datetime
from pathlib import Path

import yaml

SITE_DIR = Path(__file__).parent / "site"
TOC_FILE = SITE_DIR / "_toc.yml"
DATES_FILE = SITE_DIR / "post_dates.yml"
JS_TEMPLATE_FILE = SITE_DIR / "_templates" / "sidebar_template.js"
JS_FILE = SITE_DIR / "_static" / "js" / "custom.js"


def load_post_dates() -> dict[str, str]:
    """Map post name -> ISO date string."""
    if DATES_FILE.exists():
        data = yaml.safe_load(DATES_FILE.read_text()) or {}
        return {k: str(v) for k, v in data.items() if not k.startswith("#")}
    return {}


def get_file_date(file_path: Path, post_dates: dict[str, str], name: str) -> tuple[str, int]:
    """Get the publication (year, month) for a post."""
    date = post_dates.get(name)
    if date:
        year, month = date[:4], int(date[5:7])
        return year, month
    # Fallback: file creation time (st_birthtime on macOS)
    st = file_path.stat()
    ts = getattr(st, "st_birthtime", st.st_mtime)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y"), dt.month


def parse_toc(toc_file: Path) -> list[str]:
    """Parse the TOC file and extract notebook filenames."""
    notebooks = []
    with open(toc_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("- file:") or line.startswith("file:"):
                if line.startswith("- file:"):
                    notebook = line[7:].strip()
                else:
                    notebook = line[6:].strip()
                if notebook:
                    notebooks.append(notebook)
    return notebooks


def generate_groups(site_dir: Path, notebooks: list[str]) -> dict[str, dict[int, list[str]]]:
    """Group notebooks by publication year, then month (posts keep TOC order)."""
    post_dates = load_post_dates()
    groups: dict[str, dict[int, list[str]]] = {}
    for notebook in notebooks:
        # Skip WIP notebooks
        if notebook.startswith("WIP"):
            continue
        notebook_path = site_dir / f"{notebook}.ipynb"
        if notebook_path.exists():
            year, month = get_file_date(notebook_path, post_dates, notebook)
            groups.setdefault(year, {}).setdefault(month, []).append(notebook)
    return groups


def sort_groups(groups: dict[str, dict[int, list[str]]]) -> dict[str, dict[int, list[str]]]:
    """Sort years ascending, months ascending within each year."""
    return {
        year: dict(sorted(months.items(), key=lambda x: x[0]))
        for year, months in sorted(groups.items(), key=lambda x: int(x[0]))
    }


def main():
    notebooks = parse_toc(TOC_FILE)
    groups = sort_groups(generate_groups(SITE_DIR, notebooks))

    print("Generated year/month groupings from file dates:")
    for year, months in groups.items():
        month_summary = ", ".join(f"{month:02d}: {len(files)}" for month, files in months.items())
        print(f"  {year}: {month_summary}")

    if not JS_TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template file not found: {JS_TEMPLATE_FILE}")

    template = JS_TEMPLATE_FILE.read_text()
    result = template.replace("YEARGROUPS_PLACEHOLDER", str(groups))
    JS_FILE.write_text(result)
    print(f"Updated {JS_FILE}")


if __name__ == "__main__":
    main()
