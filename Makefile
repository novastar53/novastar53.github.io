################################################################################
# Makefile
################################################################################

#-------------------------------------------------------------------------------
# Environment
#-------------------------------------------------------------------------------

VENV_ROOT := .venv
VENV := $(VENV_ROOT)/bin/activate

################################################################################
# Targets
################################################################################

all: venv init build deploy

venv:
	python -m venv $(VENV_ROOT)

init:
	. $(VENV) && uv sync

build: 
	export PATH=$(PATH):/Library/TeX/texbin/latex
	. $(VENV) && jupyter-book build site/
	cp -r site/media site/_build/html/ # TODO: Find a better way to include the manim media dir 

deploy: build
	. $(VENV) && cd site && ghp-import -n -p -f _build/html

clean: 
	. $(VENV) && jupyter-book clean -a site/

.PHONY: all venv init build deploy clean

