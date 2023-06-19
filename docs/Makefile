SHELL := /bin/bash
SOURCEDIR = source
BUILDDIR = build

all:
	sphinx-build -M html "$(SOURCEDIR)" "$(BUILDDIR)" --keep-going

clean:
	rm -rf "$(BUILDDIR)"
