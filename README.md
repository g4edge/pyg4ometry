# pyg4ometry

Python code for rapid creation and conversion of radiation transport Monte
Carlo (Geant4 and Fluka) geometries.

[![PyPI](https://img.shields.io/pypi/v/pyg4ometry?logo=pypi)](https://pypi.org/project/pyg4ometry/)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/g4edge/pyg4ometry?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/checks-status/g4edge/pyg4ometry/main?label=main%20branch&logo=github)](https://github.com/g4edge/pyg4ometry/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/codecov/c/github/g4edge/pyg4ometry?logo=codecov)](https://app.codecov.io/gh/g4edge/pyg4ometry)
![GitHub issues](https://img.shields.io/github/issues/g4edge/pyg4ometry?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/g4edge/pyg4ometry?logo=github)
![License](https://img.shields.io/github/license/g4edge/pyg4ometry)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10449301.svg)](https://doi.org/10.5281/zenodo.10449301)
[![Read the Docs](https://img.shields.io/readthedocs/pyg4ometry?logo=readthedocs)](https://pyg4ometry.readthedocs.io)

## Quick start

_pyg4ometry_ is a very capable package to do many tasks related
to Geant4/Fluka/MCNP geometry:

- Python scripting to create and assemble geometries
- Loading, editing and writing GDML
- Load and tessellate CAD geometry and export to GDML
- Load ROOT geometry and convert to GDML
- Powerful VTK viewer of geometries
- Converting from GDML to FLUKA and MCNP
- Exporting mesh geometries from GDML to VTP, OBJ, VRML etc.
- Python bindings to CGAL allowing complex mesh manipulation (e.g. hole filling, remeshing)

All with few lines of Python code!

```py
import pyg4ometry as pg4
from g4edgetestdata import G4EdgeTestData

g4data = G4EdgeTestData()
# define a geometry registry
reg = pg4.geant4.Registry()

# build the world volume
world_s = pg4.geant4.solid.Orb("WorldAir", 1.5, reg, lunit="cm")
world_l = pg4.geant4.LogicalVolume(world_s, "G4_AIR", "WorldAir", reg)
reg.setWorld(world_l)

# import an STL file
reader = pg4.stl.Reader(g4data["stl/utah_teapot.stl"], registry=reg)
teapot_s = reader.getSolid()

# place the teapot in the world
teapot_l = pg4.geant4.LogicalVolume(teapot_s, "G4_Cu", "UtahTeapot", reg)
pg4.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], teapot_l, "UtahTeapot", world_l, reg)

# export to GDML file "geometry.gdml"
writer = pg4.gdml.Writer()
writer.addDetector(reg)
writer.write("./geometry.gdml")

# start an interactive VTK viewer instance
viewer = pg4.visualisation.VtkViewer()
viewer.addLogicalVolume(reg.getWorldVolume())
viewer.view()
```

Check out our video tutorial for more:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/OPvQFZsFvhs/0.jpg)](https://www.youtube.com/watch?v=OPvQFZsFvhs)

## How to Install

Pre-built _pyg4ometry_ wheels can be installed [from PyPI](https://pypi.org/project/pyg4ometry)
using pip:

```
pip install pyg4ometry
```

If you cannot find wheels for your operating system / architecture,
please [open an issue](https://github.com/g4edge/pyg4ometry/issues).
Building from source requires some non-Python software dependencies.
More documentation can be found in the
[installation guide](https://pyg4ometry.readthedocs.io/en/stable/manual/installation.html) in the manual.

## Many people and groups are using _pyg4ometry_

- Geometries for BDSIM Geant4 simulation of accelerators
- [LEGEND experiment](https://indico.cern.ch/event/1252095/contributions/5592424/attachments/2730430/4746429/202310-PyHEP.pdf)
- [FASER2 detector](https://cds.cern.ch/record/2893550)
- CERN North area
- [Moller](https://www.lucbarrett.info/Poster.pdf)
- Proton therapy beam lines

## Referencing and Citation

To support the development and maintenance of _pyg4ometry_, please cite it!
Any publications including simulations made using this software must cite
the _pyg4ometry_ paper:

> S.D. Walker, A. Abramov, L.J. Nevay, W. Shields, S.T. Boogert,
> “pyg4ometry: A Python library for the creation of Monte Carlo radiation transport physical geometries”,
> Computer Physics Communications 272 108228 (2022). DOI: [10.1016/j.cpc.2021.108228](https://doi.org/10.1016/j.cpc.2021.108228)

and the Zenodo release: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10449301.svg)](https://doi.org/10.5281/zenodo.10449301)

Citation information can be also obtained on GitHub by selecting “Cite this repository” in the sidebar on the right.
