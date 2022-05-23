SOURCEDIR = source
BUILDDIR = build

# docs for all project versions will be placed here
BUILDDIRALL = $(BUILDDIR)/allver/html

# list in source/.py_api_exclude files or directories that should be excluded
# from the API auto-generated documentation. No regex allowed
PY_SOURCE_EXCLUDE = $(shell cat source/.py_api_exclude)

all: apidoc
	sphinx-build -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W --keep-going

allver:
	sphinx-multiversion "$(SOURCEDIR)" "$(BUILDDIRALL)"
	cp source/_assets/redirect.html "$(BUILDDIRALL)/index.html"

allver-info:
	sphinx-multiversion --dump-metadata "$(SOURCEDIR)" "$(BUILDDIRALL)"

apidoc: clean-apidoc
	sphinx-apidoc --private --module-first --force --output-dir "$(SOURCEDIR)/generated" ../src/pkgplaceholder $(PY_SOURCE_EXCLUDE)

clean-apidoc:
	rm -rf "$(SOURCEDIR)/generated"

clean: clean-apidoc
	rm -rf "$(BUILDDIR)"
