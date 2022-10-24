import pyg4ometry as _pyg
import numpy as _np
import pyg4ometry.vtk as _vtk
import pyg4ometry.gdml as _gdml
import math as _math

#
#          safety       safety 
# |<- 20 cm ->|<- 10 cm ->|<- 10 cm ->|
#   crystal       pmt        base
#       |          |            |
#       0 

def simpleDetector(vtkViewer = True, gdmlWriter = True) :
    zero           = _pyg.geant4.Parameter("zero",0)
    safety         = _pyg.geant4.Parameter("safety",1e-12)
    
    # calorimeter crystal 
    cc_material    = "G4_GLASS_LEAD"
    cc_length      = _pyg.geant4.Parameter("cc_length",20)
    cc_xsize       = _pyg.geant4.Parameter("cc_xsize",5)
    cc_ysize       = _pyg.geant4.Parameter("cc_ysize",5)

    # pmt 
    pmt_material    = "G4_Al"
    pmt_length      = _pyg.geant4.Parameter("pmt_length",10)
    pmt_radius      = _pyg.geant4.Parameter("pmt_radius",4)
    pmt_position    = _pyg.geant4.ParameterVector("pmt_position",[zero,zero,cc_length/2.0+pmt_length/2.0+safety])

    # pmt base
    bas_material    = "G4_Al"
    bas_length      = _pyg.geant4.Parameter("bas_length",10)
    bas_radius      = _pyg.geant4.Parameter("bas_radius",4.5)
    bas_position    = _pyg.geant4.ParameterVector("bas_position",[zero,zero,cc_length/2.0+pmt_length+bas_length/2.0+2*safety])
    
    ##############################
    # world solid
    ##############################
    world_solid    = _pyg.geant4.solid.Box("sub_world_solid",500,500,500)
    world_logical  = _pyg.geant4.LogicalVolume(world_solid,"G4_Galactic","sub_world_logical")    

    cc_solid       = _pyg.geant4.solid.Box("cc_solid",cc_xsize/2.0,cc_ysize/2.0,cc_length/2.0)
    cc_logical     = _pyg.geant4.LogicalVolume(cc_solid,cc_material,"cc_logical")
    cc_physical    = _pyg.geant4.PhysicalVolume([0,0,0],[0,0,0],cc_logical,"cc_physical",world_logical)

    pmt_solid       = _pyg.geant4.solid.Tubs("pmt_solid",0,pmt_radius,pmt_length/2.0,0,_math.pi*2)
    pmt_logical     = _pyg.geant4.LogicalVolume(pmt_solid,pmt_material,"pmt_logical")
    pmt_physical    = _pyg.geant4.PhysicalVolume([0,0,0],pmt_position,pmt_logical,"pmt_physical",world_logical)

    bas_solid       = _pyg.geant4.solid.Tubs("bas_solid",0,bas_radius,bas_length/2.0,0,_math.pi*2)
    bas_logical     = _pyg.geant4.LogicalVolume(bas_solid,bas_material,"bas_logical")
    bas_physical    = _pyg.geant4.PhysicalVolume([0,0,0],bas_position,bas_logical,"bas_physical",world_logical)

    ################################
    # Mesh and write output
    ################################
    # clip the world logical volume
    world_logical.setClip();

    # register the world volume
    _pyg.geant4.registry.setWorld('sub_world_logical')

    m = world_logical.pycsgmesh()

    # view mesh
    if vtkViewer :
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();    

    if gdmlWriter : 
        w = _gdml.Writer()
        w.addDetector(_pyg.geant4.registry)
        w.write('./simpleDetector.gdml')
        w.writeGmadTester('./simpleDetector.gmad')    
