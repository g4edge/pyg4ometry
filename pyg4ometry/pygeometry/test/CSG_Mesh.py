import pygeometry.geant4 as _g4
from pygeometry.pycsg.core import CSG as _CSG
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np
import cProfile as _cp
import gc as _gc

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',500,500,500)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    sphereSolid1    = _g4.solid.Sphere('sphere1', 0, 75, 0, _np.pi*2, 0, _np.pi)
    sphereLogical1  = _g4.LogicalVolume(sphereSolid1,'G4_Cu','sphereLogical1')
    spherePhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],sphereLogical1,'spherePhysical1',worldLogical)

    boxSolid1       = _g4.solid.Box('box1',60, 60, 60)
    boxLogical1     = _g4.LogicalVolume(boxSolid1,'G4_Cu','boxLogical1')
    boxPhysical1    = _g4.PhysicalVolume([0,0,0],[0,-200,0],boxLogical1,'boxPhysical1',worldLogical)

    intrSolid1      = _g4.solid.Intersection('intr1', sphereSolid1, boxSolid1, [[0,0,0],[0,0,0]])
    intrLogical1    = _g4.LogicalVolume(intrSolid1, 'G4_Cu', 'intrLogical1')
    intrPhysical1   = _g4.PhysicalVolume([0,0,0],[0,0,0],intrLogical1, 'intrLogical1', worldLogical)

    tubsSolid1    = _g4.solid.Tubs('tubs1',0,45,60,0,2*_np.pi)
    tubsLogical1  = _g4.LogicalVolume(tubsSolid1,'G4_Cu','tubsLogical1')
    tubsPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,0,0],tubsLogical1,'tubsPhysical1',worldLogical)

    uniSolid1      = _g4.solid.Union('uni1', tubsSolid1, tubsSolid1, [[_np.pi/2,0,0],[0,0,0]])
    uniLogical1    = _g4.LogicalVolume(uniSolid1, 'G4_Cu', 'uniLogical1')
    uniPhysical1   = _g4.PhysicalVolume([0,0,0],[200,0,0],uniLogical1, 'uniLogical1', worldLogical)

    uniSolid2      = _g4.solid.Union('uni2', tubsSolid1, uniSolid1, [[_np.pi/2,_np.pi/2,0],[0,0,0]])
    uniLogical2    = _g4.LogicalVolume(uniSolid2, 'G4_Cu', 'uniLogical2')
    uniPhysical2   = _g4.PhysicalVolume([0,0,0],[200,-200,0],uniLogical2, 'uniLogical2', worldLogical)

    subSolid1      = _g4.solid.Subtraction('sub1', intrSolid1, uniSolid2, [[0,0,0],[0,0,0]])
    subLogical1    = _g4.LogicalVolume(subSolid1, 'G4_Cu', 'subLogical2')
    subPhysical1   = _g4.PhysicalVolume([0,0,0],[0,200,0],subLogical1, 'subLogical1', worldLogical)


     # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')
    
    m = worldLogical.pycsgmesh()
    print m
    

    if vtkViewer : 
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();
