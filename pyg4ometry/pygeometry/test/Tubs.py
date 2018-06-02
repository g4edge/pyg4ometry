import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

# sb mac profile 14.657, 15.325, 15.522, 15.253, 15.020 (Tubs.csgmesh)

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    tubsSolid1    = _g4.solid.Tubs('tubs1',0,50,50,0,2*_np.pi)
    tubsLogical1  = _g4.LogicalVolume(tubsSolid1,'G4_Cu','tubsLogical1')
    tubsPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],tubsLogical1,'tubsPhysical1',worldLogical)

    tubsSolid2    = _g4.solid.Tubs('tubs2',0,50,50,0,_np.pi)
    tubsLogical2  = _g4.LogicalVolume(tubsSolid2,'G4_Cu','tubsLogical2')
    tubsPhysical2 = _g4.PhysicalVolume([0,0,0],[-200,0,0],tubsLogical2,'tubsPhysical2',worldLogical)

    tubsSolid3    = _g4.solid.Tubs('tubs3',0,50,50,_np.pi/3.0,_np.pi)
    tubsLogical3  = _g4.LogicalVolume(tubsSolid3,'G4_Cu','tubsLogical3')
    tubsPhysical3 = _g4.PhysicalVolume([0,0,0],[-200,200,0],tubsLogical3,'tubsPhysical3',worldLogical)

    tubsSolid4    = _g4.solid.Tubs('tubs4',25,50,50,0,2*_np.pi)
    tubsLogical4  = _g4.LogicalVolume(tubsSolid4,'G4_Cu','tubsLogical4')
    tubsPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-200,0],tubsLogical4,'tubsPhysical4',worldLogical)

    tubsSolid5    = _g4.solid.Tubs('tubs5',25,50,50,0,_np.pi)
    tubsLogical5  = _g4.LogicalVolume(tubsSolid5,'G4_Cu','tubsLogical5')
    tubsPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],tubsLogical5,'tubsPhysical5',worldLogical)

    tubsSolid6    = _g4.solid.Tubs('tubs6',25,50,50,_np.pi/3.0,_np.pi)
    tubsLogical6  = _g4.LogicalVolume(tubsSolid6,'G4_Cu','tubsLogical6')
    tubsPhysical6 = _g4.PhysicalVolume([0,0,0],[0,200,0],tubsLogical6,'tubsPhysical6',worldLogical)

    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')
    
    m = worldLogical.pycsgmesh()
    
    if vtkViewer : 
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();

    # write gdml
    if gdmlWriter : 
        w = _gdml.Writer()
        w.addDetector(_g4.registry)
        w.write('./Tubs.gdml')
        w.writeGmadTester('Tubs.gmad')        
