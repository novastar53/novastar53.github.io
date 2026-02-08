# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter Book-based data science blog (Vikram's Data Science Blog) focused on educational ML content. The site is published to https://novastar53.github.io via GitHub Pages (custom domain: blog.vikrampawar.com).

## Build Commands

```bash
# Setup
make venv        # Create Python virtual environment
make init        # Install dependencies with uv

# Development
make build       # Build static site to site/_build/html/
make deploy-local  # Serve locally on http://localhost:8000
make clean       # Remove build artifacts

# Production
make deploy      # Build and push to GitHub Pages
```

## Utilities

**Freeze notebooks** to prevent re-execution during builds:
```bash
python freeze_notebook.py site/notebook.ipynb           # Overwrite in place
python freeze_notebook.py site/notebook.ipynb output.ipynb  # Save to new file
```

This adds "no-execute" tags to all cells, useful for older notebooks with long-running computations.

**Generate sidebar** (runs automatically during build):
```bash
python generate_sidebar.py
```

Groups posts by year in the sidebar based on file creation dates. Notebooks prefixed with `WIP_` are excluded from the sidebar. The template is in `site/_static/js/sidebar_template.js`.

## Architecture

- **site/_config.yml** - Jupyter Book configuration (theme: alabaster, 1 hour execution timeout)
- **site/_toc.yml** - Table of contents defining which notebooks appear in the blog
- **site/*.ipynb** - Educational Jupyter notebooks (the actual blog posts)
- **site/media/** - Generated visualizations from Manim/Jupyter (copied to build output)
- **site/_static/** - Custom CSS (`css/custom.css`) and JS (`js/custom.js`)
- **site/CNAME** - Custom domain configuration for GitHub Pages
- **pyproject.toml** - Dependencies managed by `uv`

## Local Dependencies

The project depends on a local package `jaxpt` (referenced via wheel file at `../jaxpt/dist/jaxpt-0.1.0-py3-none-any.whl`). Builds will fail if this file is not present.

## System Dependencies

- **LaTeX** - Required for Manim animations (build expects `/Library/TeX/texbin/latex` on macOS)
- **macOS** - Sidebar generation uses `stat -f %B` to read file creation dates

## Adding New Blog Posts

1. Create a Jupyter notebook in `site/`
2. Add entry to `site/_toc.yml` under `sections:`
3. Run `make build` to verify it builds
4. Run `make deploy` to publish

Prefix notebooks with `WIP_` to exclude them from the sidebar while in development.

## Key Dependencies

- **JAX/Flax** - Primary ML framework for tutorials
- **PyTorch/TensorFlow** - Also used in some posts
- **Manim** - Mathematical animations
- **Jupyter Book** - Static site generation

## Execution Behavior

Notebooks execute automatically during build (1 hour timeout, `allow_errors: true`). To prevent execution:
- Use `freeze_notebook.py` to add no-execute tags
- Or add `"no-execute"` tag to specific cells manually
