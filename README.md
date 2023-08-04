# pyg4ometry

Python code for rapid creation and conversion of radiation transport Monte
Carlo (Geant4 and Fluka) geometries.

[![PyPI](https://img.shields.io/pypi/v/pyg4ometry?logo=pypi)](https://pypi.org/project/pyg4ometry/)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/g4edge/pyg4ometry?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/checks-status/g4edge/pyg4ometry/main?label=main%20branch&logo=github)](https://github.com/pyg4ometry/pyg4ometry/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/codecov/c/github/g4edge/pyg4ometry?logo=codecov)](https://app.codecov.io/gh/pyg4ometry/pyg4ometry)
![GitHub issues](https://img.shields.io/github/issues/g4edge/pyg4ometry?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/g4edge/pyg4ometry?logo=github)
![License](https://img.shields.io/github/license/g4edge/pyg4ometry)
[![Read the Docs](https://img.shields.io/readthedocs/pyg4ometry?logo=readthedocs)](https://pyg4ometry.readthedocs.io)

> **Warning**
>
> Work-in-progress repackaging of https://bitbucket.org/jairhul/pyg4ometry. Report issues and pull requests there.

## Installing

- `pip install pyg4ometry`

> **Warning**
> Most dependencies are available from pip but you will need to install OpenCASCADE
> cgal, mpfr, gmp, ROOT

## Building

- `git clone https://github.com/g4edge/pyg4ometry.git`
- `cd pyg4ometry`
- `pip install . ` or
- `pip install --editable .` for a version which you can edit

> **Warning**
> If you update your git clone and the pybind11 C++ has changes you will need
> to reinstall and this trigger a rebuild

## Manual

Online manual

- https://pyg4ometry.readthedocs.io/en/latest/

## Developer commands (for detailed developer notes see readthedocs)

- Building the manual
  - `pip install '.[docs]'` to install doc building dependencies
  - `cd pyg4ometry/docs`
  - `make`
- Running tests
  - `pip install '.[test]'` to install test running dependencies
  - `cd pyg4ometry/tests`
  - `pytest`
- Git commit
  - pre-commit
    - `pre-commit install` to setup pre-commit in source dir (only once)
    - `pre-commit run --all-files` run pre-commit locally
    - `pre-commit run --all-files black` run only black
  - messages
    - Start commit message with `submodule : (type of change) detailed notes`
    - e.g `pycgal : (extra functionality) more 2d mesh processing`
- Pull request
  - PR messages should just explain the change in a concise way as they will form part of the change log
    - e.g `FLUKA region viewer`
  - Update the CHANGELOG.md file for generating the release notes
