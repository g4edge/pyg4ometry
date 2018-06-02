import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 500,500,150)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    twistedTrdSolid1    = _g4.solid.TwistedTrd('twistedTrd1',0.5, 30, 10, 40, 15, 60)
    twistedTrdLogical1  = _g4.LogicalVolume(twistedTrdSolid1,'G4_Cu','twistedTrdLogical1')
    twistedTrdPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], twistedTrdLogical1,'twistedTrdPhysical1',worldLogical)

    twistedTrdSolid2    = _g4.solid.TwistedTrd('twistedTrd2',_np.pi/2, 30, 10, 40, 15, 60)
    twistedTrdLogical2  = _g4.LogicalVolume(twistedTrdSolid2,'G4_Cu','twistedTrdLogical2')
    twistedTrdPhysical2 = _g4.PhysicalVolume([0,0,0],[0,200,0], twistedTrdLogical2,'twistedTrdPhysical2',worldLogical)

    twistedTrdSolid3    = _g4.solid.TwistedTrd('twistedTrd3',0.3, 20, 5, 40, 15, 50)
    twistedTrdLogical3  = _g4.LogicalVolume(twistedTrdSolid3,'G4_Cu','twistedTrdLogical3')
    twistedTrdPhysical3 = _g4.PhysicalVolume([0,0,0],[200,0,0], twistedTrdLogical3,'twistedTrdPhysical3',worldLogical)

    twistedTrdSolid4    = _g4.solid.TwistedTrd('twistedTrd4',0.5, 50, 20, 50, 20, 60)
    twistedTrdLogical4  = _g4.LogicalVolume(twistedTrdSolid4,'G4_Cu','twistedTrdLogical4')
    twistedTrdPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], twistedTrdLogical4,'twistedTrdPhysical4',worldLogical)
    
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
        w.write('./TwistedTrd.gdml')
        w.writeGmadTester('TwistedTrd.gmad')        
