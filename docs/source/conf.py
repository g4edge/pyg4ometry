# Configuration file for the Sphinx documentation builder.

import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parents[2].resolve().as_posix())

project = "pyg4ometry"
copyright = "Royal Holloway, University of London 2023"
author = "S. Boogert, A. Abramov, A. Butcher, L. Nevay, W. Shields, S. Walker"

extensions = [
    "sphinx.ext.githubpages",
    "autoapi.extension",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx.ext.inheritance_diagram",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]

source_suffix = {
    ".rst": "restructuredtext",
}
master_doc = "index"
language = "python"

# Furo theme
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/g4edge/pyg4ometry",
    "source_branch": "main",
    "source_directory": "docs/source",
}
html_title = f"{project}"

autodoc_default_options = {"ignore-module-all": True}

# intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("http://docs.scipy.org/doc/numpy", None),
    "scipy": ("http://docs.scipy.org/doc/scipy/reference", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "matplotlib": ("http://matplotlib.org/stable", None),
}  # add new intersphinx mappings here

# sphinx-autoapi
autoapi_dirs = ["../../src"]
autodoc_typehints = "description"
