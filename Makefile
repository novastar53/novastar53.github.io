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
	. $(VENV) && jupyter-book build site/ --verbose
	cp -r site/media site/_build/html/ # TODO: Find a better way to include the manim media dir 

deploy-local:
	. $(VENV) && python -m http.server 8000 --directory site/_build/html

deploy: build
	. $(VENV) && cd site && ghp-import -n -p -f _build/html

clean: 
	. $(VENV) && jupyter-book clean -a site/

.PHONY: all venv init build deploy clean

