==================
Advanced tutorials
==================

Finding volumes
---------------

Before editing geometry it is useful to find a logical volume. The registry contains all the logical volumes
using the GDML in ``pyg4ometry/pyg4ometry/test/gdmlG4examples/ChargeExchangeMC/``

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


Edit existing geometry
----------------------

After loading some geometry it is possible to modify the memory resident geometry.
This could adjusting the parameter of a given solid or PV, or replacing entirely the
type of solid used for an LV. To edit geometry a LV instance is required

Complex geometry builder
------------------------

Having access to geometry construction in python allows the rapid construction of 
geometry using functions which return an appropriate LV. Examples of this available in 
``pyg4ometry/pyg4ometry/test/pythonCompoundExamples``

Fluka geometry scripting
------------------------

In a very similar way to geant4 geometry authoring it is possible to 
use pyg4ometry to create fluka output. To create a simple region consisting 
of a single body

.. code-block :: python
   :linenos:

   import pyg4ometry.convert as convert
   import pyg4ometry.visualisation as vi
   from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry

   freg = FlukaRegistry()

   rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
   z = Zone()
   z.addIntersection(rpp)
   region = Region("RPP_REG", material="COPPER")
   region.addZone(z)
   freg.addRegion(region)

   greg = convert.fluka2Geant4(freg)
   greg.getWorldVolume().clipSolid()

   v = vi.VtkViewer()
   v.addAxes(length=20)
   v.addLogicalVolume(greg.getWorldVolume())
   v.view()

Export scene to paraview/vtk
----------------------------

.. code-block :: python
   :linenos:
   
   import pyg4ometry
   

Export scene to unity/unreal
----------------------------

The quickest way to get geometry to Unity/Unreal is to use a standard asset 
format. This takes a vtkRenderer and creates a OBJ file. The vtkRenderer 
managed within pyg4ometry from the vtkViewer class, once a geometry is created
(either from any source) then an OBJ file can be created. Taking the
example in ``pyg4ometry/pyg4ometry/test/pythonCompoundExamples/``

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

For a Fluka file, first it must be converted to geant4 and then the same process should be 
followed.

.. code-block :: python
   :linenos:
   :emphasize-lines: 3

   import pyg4ometry
   r = pyg4ometry.fluka.Reader("./Chamber.inp")
   greg = pyg4ometry.convert.fluka2geant4(r.getRegistry())
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

.. code-block :: python
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

 
