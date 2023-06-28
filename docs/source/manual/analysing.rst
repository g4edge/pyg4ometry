.. _analysing:

==================
Analysing Geometry
==================

Finding volumes
---------------

Before editing geometry it is useful to find a logical volume. The registry contains all the logical volumes
using the GDML in ``pyg4ometry/test/gdmlG4examples/ChargeExchangeMC/``

.. code-block :: python
   :linenos:

   import pyg4ometry
   r = pyg4ometry.gdml.Reader("lht.gdml")
   reg = r.getRegistry()

The ``registry`` instance ``reg`` has a member variable called ``logicalVolumeDict`` so calling

.. code-block :: python

   reg.logicalVolumeDict.keys()

should print

.. code-block :: console

   In [4]: reg.logicalVolumeDict.keys()
   Out[4]: odict_keys(['vMonitor', 'vMonitorBack', 'vTarget', 'vTargetInnerCover', 'vTargetColumn', 'vTargetInnerColumn',
                       'vTargetVacuumSpace', 'vTargetOuterCover', 'vCrystal', 'vCrystalRow', 'vCalorimeter', 'vVetoCounter',
                       'vOuterFerrumRing', 'vInnerFerrumRing', 'vInnerCuprumRing', 'vTargetWindow', 'vTargetWindowCap',
                       'vTargetWindowMylarCover', 'vTargetWindowAluminiumCover', 'vWorldVisible', 'World'])

then the LogicalVolume can be obtained simply from the dictionary

.. code-block :: python

   lv = reg.logicalVolumeDict['vTargetInnerColumn']

This ``lv`` can be used for manipulating geometry, passing to visualisers etc.


Navigating the LV-PV hierarchy
------------------------------

There is a hierarchy of LV-PVs to describe a GDML/Geant4 geometry. An LV in terms of
geometry consists of an outer solid ``lv.solid`` and ``lv.daughterVolumes``. ``lv.solid``
is one of the ``pyg4ometry.geant4.solid`` types which match the GDML/Geant4 solids. ``lv.daughterVolumes``
is a list of ``pyg4ometry.geant4.PhysicalVolumes``.

The best way to explore the methods and data members of ``pyg4ometry.geant4.LogicalVolume`` and
``pyg4ometry.geant4.PhysicalVolume`` is to explore in iPython. See cute video based on the ``lht.gdml``
example above.

Geometry Complexity Analysis
----------------------------

For a given logical volume we can get some statistics on the complexity
of the geometry. A simple class called `GeometryComplexityInformation` is
returned that has a serious of dictionaries with information. ::

  cd pyg4ometry/test/gdmlCompoundExamples/bdsim_2
  ipython
  >>> import pyg4ometry
  >>> r = pyg4ometry.gdml.Reader("22-size-variation-facetcrop-quad.gdml")
  >>> info = pyg4ometry.geant4.AnalyseGeometryComplexity(r.getRegistry().getWorldVolume())
  >>> info.printSummary()
  Types of solids
  ExtrudedSolid        : 96
  Tubs                 : 51
  Intersection         : 24
  Polyhedra            : 12
  Subtraction          : 6
  Box                  : 1

  # of daughters       count
  0                    : 152
  2                    : 19
  4                    : 12
  13                   : 6
  25                   : 1

  Depth of booleans    count
  1                    : 30

  Booleans width depth over  3
  Solid name                               : n Booleans

  >>> info. <tab>
  comp.booleanDepth      comp.nDaughtersPerLV
  comp.booleanDepthCount comp.printSummary
  comp.nDaughters        comp.solids
