# Easy Python packaging

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/ghuserplaceholder/pkgplaceholder?logo=git)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ghuserplaceholder/pkgplaceholder/pkgplaceholder/main?label=main%20branch&logo=github)
![Codecov](https://img.shields.io/codecov/c/github/ghuserplaceholder/pkgplaceholder?logo=codecov)
![GitHub issues](https://img.shields.io/github/issues/ghuserplaceholder/pkgplaceholder?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ghuserplaceholder/pkgplaceholder?logo=github)
![License](https://img.shields.io/github/license/ghuserplaceholder/pkgplaceholder)

Template for modern Python package GitHub repositories.

## Quick configuration

1. Clone the repository locally
1. Fill in your GitHub user/org name and package name:
   ```console
   $ mv pyproject-template <your package name>
   $ mv src/pkgplaceholder src/<your package name>
   $ sed -i 's|ghuserplaceholder|<your github username>|g' -- $(find . -type f -not -path "./.git/*")
   $ sed -i 's|pkgplaceholder|<your package name>|g' -- $(find . -type f -not -path "./.git/*")
   ```
1. Provide all the required information in `setup.cfg`
1. Choose a license and save it as `LICENSE` (edit `setup.cfg` accordingly)
1. Activate https://pre-commit.ci, https://codecov.io, GitHub pages (in the
   repo settings, configure it to doploy from the `gh-pages` branch), GitHub
   actions (repo settings)

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
  $ git branch -b releases/v0.1.0
  $ git push --tags
  ```

## Optional customization

* Customize the python versions to test the package against in
  `.github/workflows/main.yml`
* Edit the pre-commit hook configuration in `.pre-commit-config.yaml`
* Adapt the Sphinx configuration in `docs/source/conf.py`
