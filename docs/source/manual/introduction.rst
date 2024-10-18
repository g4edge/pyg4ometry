============
Introduction
============

This package started as an internal tool for the BDSIM and machine backgrounds
group at Royal Holloway. BDSIM is a tool to rapidly create Geant4 models of
accelerator systems. Creation of geometry is a time consuming activity and
pyg4ometry hopefully will improve the time taken to create accurate reliable
geometry flies.

Need for programmatic geometry generation
-----------------------------------------

* Non-expert user creation and maintenance of geometry
* Reduce time spent creating geometry
* Reproducibility
* Lower number of errors
* Parameterisation of geometry
* Visualisation of geometry
* Overlap checking
* Import from other geometry packages

Geant4 key concepts
-------------------

* **solid** - describes shape only.
* **logical volume** - a solid (shape) plus a material. Practically, in Geant4
  it can include fields, regions, visualisation attributes and user limits.
* **physical volume** - a placement of a logical volume. A 'stamp' out of the logical volume. It
  is uniquely identified by an associated integer called "copy number".
* **placement** - the term placement is used often to describe a physical volume. They
  are one and the same.
* **geometry reuse** - individual solids and logical volumes are encouraged to be reused. For
  example a row of copper boxes all the same would require only 1x solid and 1x logical volume
  with `N` placements (also known as physical volumes).

Geometry key concepts
---------------------

* Constructive Solid Geometry (CSG)
* Boolean operations
* Boundary representation (B-REP)
* Boundary mesh

Implementation concepts
-----------------------

.. _introduction-registry:

Registry
********

In pyg4ometry and in GDML we must uniquely identify objects by their associated name. However,
in Geant4 (in C++) objects are uniquely identified by their memory address (pointer) and even
for objects that have a name parameter, there is no requirement for these to be unique.

To resolve this we have the concept of a registry. This is a holder for all the definitions
for a given set of geometry. It can be thought of as a namespace. It will protect against
duplicate names that would prevent writing the geometry to GDML.

A :code:`pyg4ometry.geant4.Registry` instance holds dictionaries to all solids, logical volumes
and other objects, but also a nominated 'top volume' - the world volume. This needn't be the
"world" as such, but is identified as the topmost part of the geometry.

When loading geometry, the typical result is a registry that contains all definitions and
a top volume.

It is possible to merge two registries and all the name conflicts will be explicitly resolved.
See :ref:`combining`.

* Parameter
* ParameterVector
* Pycsg
