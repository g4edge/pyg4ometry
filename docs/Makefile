SHELL := /bin/bash
SOURCEDIR = source
BUILDDIR = build

all: apidoc
	sphinx-build -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W --keep-going

apidoc: clean-apidoc
	sphinx-apidoc --private --module-first --force \
      --output-dir "$(SOURCEDIR)/generated" \
      ../src/pyg4ometry ../src/pyg4ometry/_version.py

clean-apidoc:
	rm -rf "$(SOURCEDIR)/generated"

clean: clean-apidoc
	rm -rf "$(BUILDDIR)"
