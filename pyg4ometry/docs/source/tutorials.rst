=========
Tutorials
=========

Geant4 python scripting 
-----------------------

Making use of pyg4ometry requires the following modules 

.. code-block :: python

   import pyg4ometry      as pyg  # geant4  
   import pyg4ometry.vtk  as vtk  # vistualisation tool kit commands
   import pyg4ometry.gdml as gdml # gdml io

The standard math and numpy modules are also very useful

.. code-block :: python

   import numpy as np
   import math  as math

To make a simple geometery of a boolean subtraction solid (a cube with a cylinder removed in the centre)


A triangular mesh is generated from any physical ``volume`` by the following command 

.. code-block :: python

   m = volume.pycsgmesh()

Given an output from ``m = volume.pycsgmesh()`` it can be viewed in the ``vtk`` viewer with the following example

.. code-block :: python

    v = pyg4ometry.vtk.Viewer()  
    v.addPycsgMeshList(m)
    v.view();

To write an STL file from ``m = volume.pycshmesh()`` 

.. code-block :: python

    vtkConverter = vtk.Convert()
    vtkPD        =  vtkConverter.MeshListToPolyData(m)
    r = vtk.WriteSTL("file.stl",vtkPD)

To write an GDML file file 

.. code-block :: python

    w = _gdml.Writer()
    w.addDetector(pyg.geant4.registry)
    w.write('./file.gdml')
    w.writeGmadTester('./file.gmad')  


GDML input 
----------

STL input 
---------

STEP/STP input
---------------

FLUKA input 
-----------

STL output
----------