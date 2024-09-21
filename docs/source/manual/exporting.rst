.. _exporting:

==================
Exporting Geometry
==================


Registry and GDML Output
------------------------

Strictly speaking a registry class to store all of the GDML is not required.
As with normal Geant4 given a ``lv`` pointer it should possible to form an aggregation
hierarchy that contains all necessary objects. Now GDML breaks this as the
structure is built up using ``name`` tags. For example a placement requires
a position. In Geant4 this would just be a pointer to an transformation object, but GDML
has two mechanisms to represent this, firstly child nodes of a PhysicalVolume tag
or secondly a position define, see below

The registry class is a storage class for a complete GDML file. At the
construction stage of almost all objects a registry is required. If the
object is added to the registry then it will appear explicitly in the GDML
output

GDML Output
-----------

To write an GDML file, a :code:`pyg4ometry.geant4.registry` instance (:code:`reg` here),
must be supplied.

.. code-block :: python
   :emphasize-lines: 3
   :linenos:

   import pyg4ometry
   w = pyg4ometry.gdml.Writer()
   w.addDetector(reg)
   w.write('file.gdml')
   # make a quick bdsim job for the one component in a beam line
   w.writeGmadTester('file.gmad', 'file.gdml')

Export scene to Paraview/Vtk
----------------------------

The viewers can export to the VTK/Paraview VTP file format

.. code-block :: python
   :linenos:

   import pyg4ometry
   r = pyg4ometry.gdml.Reader("./Chamber.gdml")
   l = r.getRegistry().getWorldVolume()
   v = pyg4ometry.visualisation.VtkViewer()
   v.addLogicalVolume(l)
   v.exportVTPScene("Chamber")


Export scene to unity/unreal/blender
------------------------------------

The quickest way to get geometry to Unity/Unreal/blender etc is to use a standard asset
format. This takes a vtkRenderer and creates a OBJ file. The vtkRenderer
managed within pyg4ometry from the VtkViewer class, once a geometry is created
(either from any source) then an OBJ file can be created. Taking the
example in ``pyg4ometry/test/pythonCompoundExamples/``

.. code-block :: python
   :linenos:
   :emphasize-lines: 6

   import pyg4ometry
   r = pyg4ometry.gdml.Reader("./Chamber.gdml")
   l = r.getRegistry().getWorldVolume()
   v = pyg4ometry.visualisation.VtkViewer()
   v.addLogicalVolume(l)
   v.exportOBJScene("Chamber")

``obj`` files are written ``Chamber.obj`` and ``Chamber.mtl``.

For a FLUKA file, first it must be converted to Geant4 and then the same process should be
followed.

.. code-block :: python
   :linenos:
   :emphasize-lines: 3

   import pyg4ometry
   r = pyg4ometry.fluka.Reader("./Chamber.inp")
   greg = pyg4ometry.convert.fluka2Geant4(r.getRegistry())
   l = greg.getWorldVolume()
   v = pyg4ometry.visualisation.VtkViewer()
   v.addLogicalVolume(l)
   v.exportOBJScene("Chamber")

As the meshing might need to changed for the visualisation application,
the parameters for the meshing for each solid might need to changed.

An ``obj`` file for an entire experiment does not help with work flows where meshes
have to be UV-ed and textured. Tools like Blender and Gaffer can be used for this workload
but require meshes for each object and their placement. To enable there is a special
writer

.. code-block:: python
   :linenos:
   :emphasize-lines: 4-6

   import pyg4ometry

   r = pyg4ometry.gdml.Reader("./Chamber.gdml")
   l = r.getRegistry().getWorldVolume()
   w = pyg4ometry.visualisation.RenderWriter()
   w.addLogicalVolumeRecursive(l)
   w.write("./SphericalChamber")

The directory ``SphericalChamber`` contains all the meshes in OBJ format along
with an instance file ``0_instances.dat`` which contains a row for each
instance of a mesh.
