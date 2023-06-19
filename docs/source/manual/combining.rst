.. _combining:

==================
Combining Geometry
==================


There are ways to incorporate geometry from multiple sources in GDML. This has potentially
lots of problems as each file needs to be a well formed GDML file and care has to be taken
with degenerate names from the different sources. For example a volume can be extracted
from GdmlFile1 and added to GdmlFile2, clearly all solids, materials and variables need
to also transferred. For this example we need two GDML files, so ``pyg4ometry/test/pythonGeant4/T001_Box.py``
and ``pyg4ometry/test/pythonGeant4/T002_Tubs.py``, so run them

.. code-block :: python
   :linenos:

   import T001_Box
   T001_Box.Test(True,True)

   import T002_Tubs
   T002_Tubs(True,True)

This will create two GDML files ``T001_Box.gdml`` and ``T002_Tubs.gdml``. It is possible to
find the volumes contained in each file (using the tubs gdml file as the example)
by performing the following

.. code-block :: python
   :linenos:

   import pyg4ometry
   r = pyg4ometry.gdml.Reader("T002_Tubs.gdml")
   reg = r.getRegistry()

   # printing the names of the logical volumes
   print(reg.logicalVolumeDict.keys())

   # printing the names of the physical volumes
   print(reg.physicalVolumeDict.keys())

   lv = reg.logicalVolume["tl"]

Now merging the ``tl`` logicalVolume (which is a simple tubs) with the box gdml file

.. code-block :: python
   :linenos:
   :emphasize-lines: 13

   import pyg4ometry
   r1 = pyg4ometry.gdml.Reader("T001_Box.gdml")
   reg1 = r1.getRegistry()

   r2 = pyg4ometry.gdml.Reader("T002_Tubs.gdml")
   reg2 = r2.getRegistry()

   lv = reg2.logicalVolumeDict["tl"]

   # create physical volume with placement
   pv = pyg4ometry.geant4.PhysicalVolume([0,0,0],[50,0,0], lv, "tl_pv", reg1.getWorldVolume(), reg1)

   reg1.addVolumeRecursive(pv)

   # gdml output
   w = pyg4ometry.gdml.Writer()
   w.addDetector(reg1)
   w.write("MergeRegistry.gdml")

.. note::
   In the example two registry objects are created and objects from reg2 are merged into reg1. Of course one
   registry might be formed by pyg4ometry commands opposed created from a file.

.. warning::
   The pv needs to added with addVolumeRecursive otherwise it is possible that GDML definitions which lv depends
   on are not transferred over.
