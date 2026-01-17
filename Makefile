################################################################################
# Makefile
################################################################################

#-------------------------------------------------------------------------------
# Environment
#-------------------------------------------------------------------------------

VENV_ROOT := .venv
VENV := $(VENV_ROOT)/bin/activate
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION := python

################################################################################
# Targets
################################################################################

all: venv init build deploy

venv:
	python -m venv $(VENV_ROOT)

init:
	. $(VENV) && uv sync

build:
	export PATH="$(PATH):/Library/TeX/texbin/latex"
	. $(VENV) && python generate_sidebar.py
	. $(VENV) && jupyter-book build site/ --verbose
	cp -r site/_static/* site/_build/html/_static/  # Ensure latest static files are used
	cp -r site/media site/_build/html/ # TODO: Find a better way to include the manim media dir
	cp CNAME site/_build/html/  # Preserve custom domain for GitHub Pages

deploy-local:
	. $(VENV) && python -m http.server 8000 --directory site/_build/html

deploy: build
	. $(VENV) && cd site && ghp-import -n -p -f _build/html

clean: 
	. $(VENV) && jupyter-book clean -a site/

.PHONY: all venv init build deploy clean

