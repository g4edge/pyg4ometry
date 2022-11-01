import math as _math


import pyg4ometry as _pyg
import pyg4ometry.gdml as _gdml
import pyg4ometry.vtk as _vtk

#  <----- cj_length1 ------>
#  -------------------------   |x cj_width
#   \                     /    | cj_thick
#    \                   /     |
#     ------------------       |
#     <-- cj_length2 -->
#     ------------------
#    /                   \
#   /                     \
#  -------------------------
#


def simpleCollimator(vtkViewer=True, gdmlWriter=True):
    zero = _pyg.geant4.Parameter("zero", 0.0)
    ucj_yposition = _pyg.geant4.Parameter("ucj_yposition", 50)
    lcj_yposition = _pyg.geant4.Parameter("lcj_yposition", -50)
    cj_width = _pyg.geant4.Parameter("cj_width", 20.0)
    cj_thick = _pyg.geant4.Parameter("cj_thick", 5.0)
    cj_length1 = _pyg.geant4.Parameter("cj_length1", 50.0)
    cj_length2 = _pyg.geant4.Parameter("cj_length2", 30.0)

    # upper collimator jaw
    cj_material = "G4_Cu"
    ucj_position = _pyg.geant4.ParameterVector(
        "ucj_position", [zero, ucj_yposition, zero]
    )
    lcj_position = _pyg.geant4.ParameterVector(
        "lcj_position", [zero, lcj_yposition, zero]
    )

    ##############################
    # world solid
    ##############################
    world_solid = _pyg.geant4.solid.Box("sub_world_solid", 500, 500, 500)
    world_logical = _pyg.geant4.LogicalVolume(
        world_solid, "G4_Galactic", "sub_world_logical"
    )

    cj_solid = _pyg.geant4.solid.Trd(
        "upper_collimator_jaw", cj_width, cj_width, cj_length1, cj_length2, cj_thick
    )
    cj_logical = _pyg.geant4.LogicalVolume(cj_solid, cj_material, "cj_logical")
    ucj_physical = _pyg.geant4.PhysicalVolume(
        [-_math.pi / 2.0, 0, 0], ucj_position, cj_logical, "ucj_physical", world_logical
    )
    lcj_physical = _pyg.geant4.PhysicalVolume(
        [_math.pi / 2.0, 0, 0], lcj_position, cj_logical, "lcj_physical", world_logical
    )

    ################################
    # Mesh and write output
    ################################
    # clip the world logical volume
    world_logical.setClip()

    # register the world volume
    _pyg.geant4.registry.setWorld("sub_world_logical")

    m = world_logical.pycsgmesh()

    # view mesh
    if vtkViewer:
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view()

    if gdmlWriter:
        w = _gdml.Writer()
        w.addDetector(_pyg.geant4.registry)
        w.write("./simpleCollimator.gdml")
        w.writeGmadTester("./simpleCollimator.gmad")
