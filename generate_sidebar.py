#!/usr/bin/env python3
"""Generate sidebar year groupings from post dates.

Dates come from site/post_dates.yml (the source of truth, since CI
checkouts lose file-creation times); falls back to file birth time.
"""

import os
import re
from datetime import datetime
from pathlib import Path

import yaml

SITE_DIR = Path(__file__).parent / "site"
TOC_FILE = SITE_DIR / "_toc.yml"
DATES_FILE = SITE_DIR / "post_dates.yml"
JS_TEMPLATE_FILE = SITE_DIR / "_static" / "js" / "sidebar_template.js"
JS_FILE = SITE_DIR / "_static" / "js" / "custom.js"


def load_post_dates() -> dict[str, str]:
    """Map post name -> ISO date string."""
    if DATES_FILE.exists():
        data = yaml.safe_load(DATES_FILE.read_text()) or {}
        return {k: str(v) for k, v in data.items() if not k.startswith("#")}
    return {}


def get_file_year(file_path: Path, post_dates: dict[str, str], name: str) -> str:
    """Get the publication year for a post."""
    date = post_dates.get(name)
    if date:
        return date[:4]
    # Fallback: file creation time (st_birthtime on macOS)
    st = file_path.stat()
    ts = getattr(st, "st_birthtime", st.st_mtime)
    return datetime.fromtimestamp(ts).strftime("%Y")


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


def generate_year_groups(site_dir: Path, notebooks: list[str]) -> dict[str, list[str]]:
    """Group notebooks by their publication year."""
    post_dates = load_post_dates()
    year_groups = {}
    for notebook in notebooks:
        # Skip WIP notebooks
        if notebook.startswith("WIP"):
            continue
        notebook_path = site_dir / f"{notebook}.ipynb"
        if notebook_path.exists():
            year = get_file_year(notebook_path, post_dates, notebook)
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(notebook)
    return year_groups


def sort_years(year_groups: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    """Sort years in ascending order."""
    return sorted(year_groups.items(), key=lambda x: int(x[0]))


def main():
    notebooks = parse_toc(TOC_FILE)
    year_groups = generate_year_groups(SITE_DIR, notebooks)
    year_groups_sorted = sort_years(year_groups)

    print("Generated year groupings from file dates:")
    for year, files in year_groups_sorted:
        print(f"  {year}: {len(files)} posts")

    if not JS_TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template file not found: {JS_TEMPLATE_FILE}")

    template = JS_TEMPLATE_FILE.read_text()
    json_str = str({year: files for year, files in year_groups_sorted})
    result = template.replace("YEARGROUPS_PLACEHOLDER", json_str)
    JS_FILE.write_text(result)
    print(f"Updated {JS_FILE}")


if __name__ == "__main__":
    main()
