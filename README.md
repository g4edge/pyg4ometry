# pyproject template

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/gipert/pyg4ometry?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/gipert/pyg4ometry/pyg4ometry/main?label=main%20branch&logo=github)](https://github.com/gipert/pyg4ometry/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/codecov/c/github/gipert/pyg4ometry?logo=codecov)](https://app.codecov.io/gh/gipert/pyg4ometry)
![GitHub issues](https://img.shields.io/github/issues/gipert/pyg4ometry?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/gipert/pyg4ometry?logo=github)
![License](https://img.shields.io/github/license/gipert/pyg4ometry)
[![Read the Docs](https://img.shields.io/readthedocs/pyg4ometry?logo=readthedocs)](https://pyg4ometry.readthedocs.io)

Template for modern Python package GitHub repositories.

## Quick configuration

1. Clone the repository locally
1. Fill in your GitHub user/org name and package name:
   ```console
   $ mv pyproject-template <your package name>
   $ mv src/pyg4ometry src/<your package name>
   $ sed -i 's|gipert|<your github username>|g' -- $(find . -type f -not -path "./.git/*")
   $ sed -i 's|pyg4ometry|<your package name>|g' -- $(find . -type f -not -path "./.git/*")
   ```
1. Provide all the required information in `setup.cfg`
1. Choose a license and save its statement in `LICENSE` (edit `setup.cfg` accordingly)
1. Activate
    * https://pre-commit.ci
    * https://codecov.io
    * https://readthedocs.io (activate versions for which you want docs to be build)
    * GitHub actions (in the repository settings)

## Quick start

* Install:
  ```console
  $ pip install .
  $ pip install .[test] # get ready to run tests
  $ pip install .[docs] # get ready to build documentation
  $ pip install .[all]  # get all from above
  ```
* Build documentation:
  ```console
  $ cd docs
  $ make        # build docs for the current version
  $ make allver # build docs for all supported versions
  ```
* Run tests with `pytest`
* Run pre-commit hooks with `pre-commit run --all-files`
* Release a new version:
  ```console
  $ git tag v0.1.0
  $ git checkout -b releases/v0.1 # to apply patches, if needed, later
  $ git push --tags
  ```

## Optional customization

* Customize the python versions to test the package against in
  `.github/workflows/main.yml`
* Edit the pre-commit hook configuration in `.pre-commit-config.yaml`. A long
  list of hooks can be found [here](https://pre-commit.com/hooks.html)
* Adapt the Sphinx configuration in `docs/source/conf.py`
