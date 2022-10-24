import pyg4ometry as _pyg
import numpy as _np
import pyg4ometry.vtk as _vtk
import pyg4ometry.gdml as _gdml
import math as _math

def simpleBody(vtkViewer = True, stlWriter = True, gdmlWriter = True) :
    worldSolid      = _pyg.geant4.solid.Box('worldBox',500,500,500)
    worldLogical    = _pyg.geant4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    sphereSolid1    = _pyg.geant4.solid.Sphere('sphere1', 0, 75.0, 0, _np.pi*2, 0, _np.pi, nslice=20, nstack=20)
    sphereLogical1  = _pyg.geant4.LogicalVolume(sphereSolid1,'G4_Cu','sphereLogical1')
    spherePhysical1 = _pyg.geant4.PhysicalVolume([0,0,0],[-200,-200,0],sphereLogical1,'spherePhysical1',worldLogical)

    boxSolid1       = _pyg.geant4.solid.Box('box1',60, 60, 60)
    boxLogical1     = _pyg.geant4.LogicalVolume(boxSolid1,'G4_Cu','boxLogical1')
    boxPhysical1    = _pyg.geant4.PhysicalVolume([0,0,0],[0,-200,0],boxLogical1,'boxPhysical1',worldLogical)

    intrSolid1      = _pyg.geant4.solid.Intersection('intr1', sphereSolid1, boxSolid1, [[0,0,0],[0,0,0]])
    intrLogical1    = _pyg.geant4.LogicalVolume(intrSolid1, 'G4_Cu', 'intrLogical1')
    intrPhysical1   = _pyg.geant4.PhysicalVolume([0,0,0],[0,0,0],intrLogical1, 'intrPhysical1', worldLogical)

    tubsSolid1      = _pyg.geant4.solid.Tubs('tubs1',0,45,60,0,2*_np.pi,nslice=32)
    tubsLogical1    = _pyg.geant4.LogicalVolume(tubsSolid1,'G4_Cu','tubsLogical1')
    tubsPhysical1   = _pyg.geant4.PhysicalVolume([0,0,0],[-200,0,0],tubsLogical1,'tubsPhysical1',worldLogical)

    uniSolid1       = _pyg.geant4.solid.Union('uni1', tubsSolid1, tubsSolid1, [[_np.pi/2,0,0],[0,0,0]])
    uniLogical1     = _pyg.geant4.LogicalVolume(uniSolid1, 'G4_Cu', 'uniLogical1')
    uniPhysical1    = _pyg.geant4.PhysicalVolume([0,0,0],[200,0,0],uniLogical1, 'uniPhysical1', worldLogical)

    uniSolid2       = _pyg.geant4.solid.Union('uni2', tubsSolid1, uniSolid1, [[_np.pi/2,_np.pi/2,0],[0,0,0]])
    uniLogical2     = _pyg.geant4.LogicalVolume(uniSolid2, 'G4_Cu', 'uniLogical2')
    uniPhysical2    = _pyg.geant4.PhysicalVolume([0,0,0],[200,-200,0],uniLogical2, 'uniPhysical2', worldLogical)

    subSolid1       = _pyg.geant4.solid.Subtraction('sub1', intrSolid1, uniSolid2, [[0,0,0],[0,0,0]])
    subLogical1     = _pyg.geant4.LogicalVolume(subSolid1, 'G4_Cu', 'subLogical1')
    subPhysical1    = _pyg.geant4.PhysicalVolume([0,0,0],[0,200,0],subLogical1, 'subPhysical1', worldLogical)


     # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _pyg.geant4.registry.setWorld('worldLogical')

    # mesh the problem
    m = worldLogical.pycsgmesh()
    
    if vtkViewer : 
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();    

    if gdmlWriter : 
        w = _gdml.Writer()
        w.addDetector(_pyg.geant4.registry)
        w.write('./simpleBody.gdml')
        w.writeGmadTester('./simpleBody.gmad')    

    if stlWriter :
        m1 = subLogical1.pycsgmesh()
        vtkConverter = _vtk.Convert()
        vtkPD        = vtkConverter.MeshListToPolyData(m1)
        _vtk.WriteSTL("./simpleBody.stl",vtkPD)        
