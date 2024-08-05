.. _comparing:

==================
Comparing Geometry
==================

When converting or preparing geometry, it is useful to compare to other
geometry to validate work. Examples of use include:

* validating changes to existing pyg4ometry scripts
* validating geometry created in pyg4ometry versus another source
* comparing different representations
* validating conversion between formats

pyg4ometry provides a set of tests for comparing two geometry "trees" that
are loaded into memory. Each hierarchy of geometry is navigated and a variety
of user-selectable tests are carried out. A result class with details of tests
carried out and their outcome is produced and can be easily printed or inspected
programmatically.

When we compare 2 things, we use the terminology **reference** and **other** for
each. When we need to identify a pair, we use the reference object name. Reference
is the object that is the control, or assumed to be the 'right' one.

Tests
-----

Which tests to conduct are defined by an instance of :code:`pyg4ometry.compare.Tests`,
which has a set of Boolean options for each test.


The available tests are described below.

.. tabularcolumns:: |p{0.20\textwidth}|p{0.50\textwidth}|

+--------------------------+------------------------------------------------+
| **Test Name**            | **Description**                                |
+==========================+================================================+
| names                    | Test whether objects have the exact same name. |
+--------------------------+------------------------------------------------+
| namesIgnorePointers      | Test whether objects have the exact same name, |
|                          | but whilst ignorign pointer suffixes such as   |
|                          | 0x1234567. Note, the geometry will load ok,    |
|                          | the name stripping is only for comparison.     |
+--------------------------+------------------------------------------------+
| nDaughters               | Test for a matching number of daughter volumes |
|                          | in a LogicalVolume or AssemblyVolume.          |
+--------------------------+------------------------------------------------+
| solidExact               | Compare the class type of every solid.         |
+--------------------------+------------------------------------------------+
| shapeExtent              | Numerically compare the size of the bounding   |
|                          | box (i.e. extent) of each solid.               |
+--------------------------+------------------------------------------------+
| shapeVolume              | Compare the volume as per the visualisation    |
|                          | mesh of each shape.                            |
+--------------------------+------------------------------------------------+
| shapeArea                | Compare the surface area as per the            |
|                          | visualisation mesh of each shape.              |
+--------------------------+------------------------------------------------+
| placement                | Numerically compare the rotation and           |
|                          | translations in each placement.                |
+--------------------------+------------------------------------------------+
| scale                    | Compare the 'scale' for a physical volume that |
|                          | can be used for a reflection. No scale is      |
|                          | equal to unit scale [1,1,1].                   |
+--------------------------+------------------------------------------------+
| copyNumber               | Compare the copy number for a physical volume. |
+--------------------------+------------------------------------------------+
| materials                | Whether to do a series of tests of materials   |
|                          | in a LogicalVolume.                            |
+--------------------------+------------------------------------------------+
| materialClassType        | If doing materials tests, compare the class    |
|                          | name of each material.                         |
+--------------------------+------------------------------------------------+
| materialCompositionType  | If doing materials tests, compare the class    |
|                          | name of each component of a material.          |
+--------------------------+------------------------------------------------+
| testDaughtersByName      | Whether to check daughter volumes by name or   |
|                          | by index. If true, then a set of overlapping   |
|                          | names is used and the matching ones that exist |
|                          | in both are compared. If false, the daughters  |
|                          | are strictly compared in numerical order.      |
+--------------------------+------------------------------------------------+

.. note:: Volumes and areas are based on the polygonal meshes generated for
	  visualisation purposes. These may not be the exact area of a perfect
	  shape, such as a sphere, but an approximation. They will however, be
	  consistently generated. Consider the tolerances also.

Tolerances
**********

When making numerical comparisons (e.g. position of a volume), we must consider
the finite numerical precision in a computer. Also, this may be useful as geometry
from another source may be practically equivalent, but not exactly at the last
decimal place.

Therefore, we include a set of tolerances for numerical comparisons that are
included in the Tests class. These are typically fractional.

.. note:: The fraction is calculated with respect to the reference value. So
	  :math:`( value_{other} - value_{reference} ) / value_{reference}`.

.. tabularcolumns:: |p{0.30\textwidth}|p{0.20\textwidth}|p{0.40\textwidth}|

+-----------------------------------+--------------------+------------------------------------------+
| **Variable Name**                 | **Default Value**  | **Description**                          |
+===================================+====================+==========================================+
| toleranceSolidParameterFraction   | 1e-3               | Maximum fractional difference for        |
|                                   |                    | any solid parameter.                     |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceSolidExtentFraction      | 1e-6               | Maximum fractional difference for        |
|                                   |                    | the calculated extent of any solid.      |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceVolumeFraction           | 1e-2               | Maximum fractional difference in volume. |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceAreaFraction             | 1e-2               | Maximum fractional difference in area.   |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceTranslationFraction      | 1e-6               | Maximum fractional difference for        |
|                                   |                    | translations in placements.              |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceScaleFraction            | 1e-3               | Maximum fractional difference in scale   |
|                                   |                    | parameters in placements.                |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceRotationFraction         | 1e-6               | Maximum fractional difference in         |
|                                   |                    | rotation angles in placements.           |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceMaterialDensityFraction  | 1e-4               | Maximum fractional difference in the     |
|                                   |                    | density of a material.                   |
+-----------------------------------+--------------------+------------------------------------------+
| toleranceMaterialMassFraction     | 1e-4               | Maximum fractional difference in the     |
|                                   |                    | mass fraction of a material component.   |
+-----------------------------------+--------------------+------------------------------------------+


Running a Comparison
--------------------

See also :ref:`geometry-compare-module` for all functions.

A comparison is run by using a function in :code:`pyg4ometry.compare`, giving it two objects
and a Tests instance. The comparison result returned is a class with a list of test results
that can be inspected and also printed.

GDML Files
**********

::

   >>> comparison = pyg4ometry.compare.gdmlFiles("file_reference.gdml", "file_other.gdml")
   >>> comparison.print()

Logical Volumes
***************

Compare two logical volumes, such as the top volume of a registry from a loaded file.

::

   >>> comparison = pyg4ometry.compare.geometry(refLV, otherLV)
   >>> comparison.print()

There are functions to compare individual objects too. These follow the same pattern. A few are:

* :code:`pyg4ometry.compare.physicalVolumes`
* :code:`pyg4ometry.compare.assemblyVolumes`
* :code:`pyg4ometry.compare.replicaVolumes`
* :code:`pyg4ometry.compare.divisionVolumes` - not implemented yet
* :code:`pyg4ometry.compare.parameterisedVolumes` - not implemented yet
* :code:`pyg4ometry.compare.materials`
* :code:`pyg4ometry.compare.solids`


Example Output
**************

For a test that failed the following is an example of output.

::

   Overall result>  TestResult.Failed
   Test>  position
   (av): a_assembly: (pv): a_a_pv1: a_a_pv1_pos: TestResult.Failed: z: (reference): 100.0, (other): -100.0

   Test>  shapeExtentBoundingBoxMin
   a_assembly_a_a_pv1: TestResult.Failed: axis-aligned bounding box lower edge: dimension: z, (reference): 85.0, (other): -115.0

   Test>  shapeExtentBoundingBoxMax
   a_assembly_a_a_pv1: TestResult.Failed: axis-aligned bounding box upper edge: dimension: z, (reference): 115.0, (other): -85.0

Seeing the Results
------------------

The return of a comparison is a :code:`pyg4ometry.compare.ComparisonResult` instance.
The most useful function here is the print function, which will print all results
but also you can print select sets of tests or only certain results.

* See :ref:`geometry-compare-module` and :code:`ComparisonResult` for details.

Examples
--------

See :code:`pyg4ometry/test/pythonGeant4/T7*.py` for examples that form the tests of this code.

Only Volume
***********

Here, two ways are shown for creating the set of tests.

::

   >>> import pyg4ometry
   >>> t = pyg4ometry.compare.Tests()
   >>> pyg4ometry.compare.Tests.printAllTestNames()
       "names"
       "namesIgnorePointer"
       "nDaughters"
       "solidExact"
       "solidExtent"
       "shapeExtent"
       "shapeVolume"
       "shapeArea"
       "placement"
       "scale"
       "copyNumber"
       "materials"
       "materialClassType"
       "materialCompositionType"
       "testDaughtersByName"
   >>> t.setAllFalse()
   >>> t.shapeVolume = True
   >>> comparison = pyg4ometry.compare.gdmlFiles("file1.gdml", "file2.gdml", t)
   >>> comparison.print()

or ::

  >>> import pyg4ometry
  >>> t2 = pyg4ometry.compare.Tests("shapeVolume")
  >>> comparison = pyg4ometry.compare.gdmlFiles("file1.gdml", "file2.gdml", t2)
  >>> comparison.print()

Removing a Test
***************

A test can be turned off by name: ::

   >>> import pyg4ometry
   >>> t = pyg4ometry.compare.Tests()
   >>> t.setFalse("names")
