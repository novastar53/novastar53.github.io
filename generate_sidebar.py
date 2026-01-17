#!/usr/bin/env python3
"""Generate sidebar year groupings from notebook file dates."""

import os
import re
from pathlib import Path

SITE_DIR = Path(__file__).parent / "site"
TOC_FILE = SITE_DIR / "_toc.yml"
JS_TEMPLATE_FILE = SITE_DIR / "_static" / "js" / "sidebar_template.js"
JS_FILE = SITE_DIR / "_static" / "js" / "custom.js"


def get_file_year(file_path: Path) -> str:
    """Get the year from a file's creation date."""
    import subprocess
    from datetime import datetime
    # Use stat to get birth time (creation date) on macOS
    result = subprocess.run(
        ["stat", "-f", "%B", str(file_path)],
        capture_output=True,
        text=True
    )
    timestamp = int(result.stdout.strip())
    return datetime.fromtimestamp(timestamp).strftime("%Y")


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
    """Group notebooks by their file modification year."""
    year_groups = {}
    for notebook in notebooks:
        # Skip WIP notebooks
        if notebook.startswith("WIP"):
            continue
        notebook_path = site_dir / f"{notebook}.ipynb"
        if notebook_path.exists():
            year = get_file_year(notebook_path)
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
