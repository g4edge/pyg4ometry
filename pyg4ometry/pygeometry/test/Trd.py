import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    trdSolid1    = _g4.solid.Trd("trd_solid1", 30, 10, 40, 15, 60)
    trdLogical1  = _g4.LogicalVolume(trdSolid1,'G4_Cu','trdLogical1')
    trdPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],trdLogical1,'trdPhysical1',worldLogical)

    trdSolid2    = _g4.solid.Trd("trd_solid2", 20, 50, 40, 15, 70)
    trdLogical2  = _g4.LogicalVolume(trdSolid2,'G4_Cu','trdLogical2')
    trdPhysical2 = _g4.PhysicalVolume([0,0,0],[-200,0,0],trdLogical2,'trdPhysical2',worldLogical)

    trdSolid3    = _g4.solid.Trd("trd_solid3", 10, 20, 30, 40, 50)
    trdLogical3  = _g4.LogicalVolume(trdSolid3,'G4_Cu','trdLogical3')
    trdPhysical3 = _g4.PhysicalVolume([0,0,0],[-200,200,0],trdLogical3,'trdPhysical3',worldLogical)

    trdSolid4    = _g4.solid.Trd("trd_solid4", 50, 40, 30, 20, 10)
    trdLogical4  = _g4.LogicalVolume(trdSolid4,'G4_Cu','trdLogical4')
    trdPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-200,0],trdLogical4,'trdPhysical4',worldLogical)

    trdSolid5    = _g4.solid.Trd("trd_solid5", 30, 15, 43, 12, 70)
    trdLogical5  = _g4.LogicalVolume(trdSolid5,'G4_Cu','trdLogical5')
    trdPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],trdLogical5,'trdPhysical5',worldLogical)
    
    trdSolid6    = _g4.solid.Trd("trd_solid6", 5, 22, 50, 20, 40)
    trdLogical6  = _g4.LogicalVolume(trdSolid6,'G4_Cu','trdLogical6')
    trdPhysical6 = _g4.PhysicalVolume([0,0,0],[0,200,0],trdLogical6,'trdPhysical6',worldLogical)

    trdSolid7    = _g4.solid.Trd("trd_solid7", 30, 10, 40, 5,40)
    trdLogical7  = _g4.LogicalVolume(trdSolid7,'G4_Cu','trdLogical7')
    trdPhysical7 = _g4.PhysicalVolume([0,0,0],[200,-200,0],trdLogical7,'trdPhysical7',worldLogical)

    trdSolid8    = _g4.solid.Trd("trd_solid8", 30, 20, 70, 25, 60)
    trdLogical8  = _g4.LogicalVolume(trdSolid8,'G4_Cu','trdLogical8')
    trdPhysical8 = _g4.PhysicalVolume([0,0,0],[200,0,0],trdLogical8,'trdPhysical8',worldLogical)

    trdSolid9    = _g4.solid.Trd("trd_solid9", 30, 20, 30, 30, 60)
    trdLogical9  = _g4.LogicalVolume(trdSolid9,'G4_Cu','trdLogical9')
    trdPhysical9 = _g4.PhysicalVolume([0,0,0],[200,200,0],trdLogical9,'trdPhysical9',worldLogical)

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
        w.write('./Trd.gdml')
        w.writeGmadTester('Trd.gmad')        
