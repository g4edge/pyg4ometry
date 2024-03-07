#!/bin/bash

brew update
# brew install --overwrite python # github's fault
brew link --overwrite python
brew install boost cgal gmp mpfr opencascade vtk root numdiff
