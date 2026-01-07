# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter Book-based data science blog (Vikram's Data Science Blog) focused on educational ML content. The site is published to https://blog.vikrampawar.com via GitHub Pages.

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

## Architecture

- **site/_config.yml** - Jupyter Book configuration (title, theme, execution settings)
- **site/_toc.yml** - Table of contents defining which notebooks appear in the blog
- **site/*.ipynb** - Educational Jupyter notebooks (the actual blog posts)
- **site/media/** - Generated visualizations from Manim/Jupyter
- **pyproject.toml** - Dependencies managed by `uv`

## Adding New Blog Posts

1. Create a Jupyter notebook in `site/`
2. Add entry to `site/_toc.yml` under `sections:`
3. Run `make build` to verify it builds
4. Run `make deploy` to publish

## Key Dependencies

- **JAX/Flax** - Primary ML framework for tutorials
- **PyTorch/TensorFlow** - Also used in some posts
- **Manim** - Mathematical animations
- **Jupyter Book** - Static site generation

## Execution Behavior

Notebooks execute automatically during build (1 hour timeout). To prevent execution:
- Use `freeze_notebook.py` to add no-execute tags
- Or add `"no-execute"` tag to specific cells manually
