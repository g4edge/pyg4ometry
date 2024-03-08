#!/bin/bash

brew update
brew install --overwrite python # github's fault

brew unlink python@3.11
brew install --overwrite python@3.11 python@3.12
brew link python@3.12

brew install boost cgal gmp mpfr opencascade vtk root numdiff
