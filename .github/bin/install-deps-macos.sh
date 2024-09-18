#!/bin/bash

brew update
brew install --overwrite python # github's fault

brew unlink python@3.11
brew install --overwrite python@3.11 python@3.12
brew link python@3.12

brew unlink node@18
brew install --overwrite node@18
brew link node@18

brew install boost cgal gmp mpfr opencascade vtk root numdiff

# needed for cibuildwheel on macos
export GMP_LIBRARIES=/opt/lib/
export GMP_INCLUDE_DIR=/opt/include/
