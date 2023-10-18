==================
Changelog (legacy)
==================

V1.0.3 - 2022 / 08 / XX

New features

* Feature extraction from tessellated meshes (with some accelerator applications)
* New opencascade based step/iges loading
* Command line interface
* Clipping of geometry when top level solid is moved (rotated/translated) or changed
* New more efficient visualisation

V1.0.2 - 2022 / 04 / 11
=======================

New Features
------------

* Function to view the difference between two logical volumes.
* Comparison test for names that ignores pointers as part of the name.
* New :code:`addSolid` function for visualiser to view a solid in the current scene
  without having a logical volume.
* Every solid now has the function :code:`convert2Tessellated` to allow it to be
  easily converted to a tessellated solid.
* Ability to 'collapse' assemblies (T. Latham)

General
-------

* All solids now have a list of units to accompany their list of variables for inspection.
* Checking angles for solids (e.g. start and sweep angle) are within :math:`2\pi` now includes
  a numerical precision tolerance that is by default floating point precision. See :code:`pyg4ometry.config.twoPiComparisonTolerance`.

Bug Fixes
---------

* Fix deployment of nist_materials.txt and nist_elements.txt package files.
* Fix loading of ROOT geometry for material and various solids. Put tests in
  for parameters that ROOT allows to be 0 but ultimately mean we cannot construct
  a valid shape from.
* Reduce length of names in Geant4 to FLUKA conversion to fix rejected names
  by FLUKA.
* Fix import of MutableMappings for Python 3.10
* Fix use of units throughout all solids for the geometry comparison tests.
* Fix units for define vectors.
* Fix copy number of physical volumes sometimes not being an integer for
  loaded GDML geometry.
* Fix reading and writing of abundance if it is an expression in a GDML material.
* Fix missing length unit for GDML writing of Generic Trap.
* Fix units in GenericTrap and Extruded solid classes.
* Fix renaming of materials (in a recursion chain) when transferring from one registry to another (T. Latham).
* Reduce verbosity of ROOT tests.
* Reduce verbostiy of comparison tests.
* Fix zero division errors in various comparison tests.

v1.0.1 - 2022 / 02 / 10
=======================

New Features
------------

* Geometry comparison tests for comparing two different geometry trees.
* Copy number for physical volumes.
* Overlap checking for assembly and replica volumes.
* Ability to analyse a registry structure and usage of objects throughout.
* ROOT geometry loader.

General
-------

* Improved documentation and docstrings.
* Refactored registry for transfer and object versus simply adding an object.
* Optimised imports.
* Cleaned up private imports throughout code to make tab complete cleaner.
* Simplified code in solids by using base class.

Bug Fixes
---------

* Improved search paths for libraries in setup.py.
* Fix merging of registries - object names won't be altered if they don't have to be.
  Fixed a clash with scales.
* Fixed conversion of FLUKA materials to Geant4 - many fixes.
* Fixed some material issues when converting Geant4 to FLUKA.


v0.9.0 - 2021 / 07 / 01
=======================

* Working version regularly used, submitted to CPC Journal for review.
* Based on CGAL for Boolean mesh operations, using pybind11, whereas previously
  was based on pycgal.
* FLUKA conversion to pyg4ometry and GDML has been reimplemented from the pyfluka
  package.
* Extensive code testing has been introduced and basic functionality documented.
* Given the strictness of CGAL, many bugs in meshing algorithms were fixed for all
  solids in `pyg4ometry.geant4.solid`.

Pre-History
===========

* v0.2.0 - 2018 / 06 / 23
* v0.1.4 - 2018 / 06 / 04
* v0.1.2 - 2018 / 06 / 03
* v0.1.1 - 2018 / 06 / 03
* v0.1.0 - 2017 / 06 / 05
* v0.4.0 - 2017 / 10 / 17
* v0.3.0 - 2017 / 07 / 06
