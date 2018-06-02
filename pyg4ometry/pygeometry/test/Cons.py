import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    consSolid1    = _g4.solid.Cons("cons_solid1", 0, 10, 0, 25, 40, 0, (4./3.)*_np.pi)
    consLogical1  = _g4.LogicalVolume(consSolid1,'G4_Cu','consLogical1')
    consPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],consLogical1,'consPhysical1',worldLogical)

    consSolid2    = _g4.solid.Cons("cons_solid2", 2, 10, 0, 5, 20, 0,_np.pi)
    consLogical2  = _g4.LogicalVolume(consSolid2,'G4_Cu','consLogical2')
    consPhysical2 = _g4.PhysicalVolume([0,0,0],[-200,0,0],consLogical2,'consPhysical2',worldLogical)

    consSolid3    = _g4.solid.Cons("cons_solid3", 5, 10, 10, 25, 40, 0, _np.pi*2)
    consLogical3  = _g4.LogicalVolume(consSolid3,'G4_Cu','consLogical3')
    consPhysical3 = _g4.PhysicalVolume([0,0,0],[-200,200,0],consLogical3,'consPhysical3',worldLogical)

    consSolid4    = _g4.solid.Cons("cons_solid4", 5, 10, 20, 25, 40, 0, (2./3.)*_np.pi)
    consLogical4  = _g4.LogicalVolume(consSolid4,'G4_Cu','consLogical4')
    consPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-200,0],consLogical4,'consPhysical4',worldLogical)

    consSolid5    = _g4.solid.Cons("cons_solid5", 5, 10, 18, 25, 60, 0, (3./4.)*_np.pi)
    consLogical5  = _g4.LogicalVolume(consSolid5,'G4_Cu','consLogical5')
    consPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],consLogical5,'consPhysical5',worldLogical)
    
    consSolid6    = _g4.solid.Cons("cons_solid6", 5, 10, 9, 14, 30, 0, (5./3.)*_np.pi)
    consLogical6  = _g4.LogicalVolume(consSolid6,'G4_Cu','consLogical6')
    consPhysical6 = _g4.PhysicalVolume([0,0,0],[0,200,0],consLogical6,'consPhysical6',worldLogical)

    consSolid7    = _g4.solid.Cons("cons_solid7",8, 13 ,9, 14, 10, 0, (3./2.)*_np.pi)
    consLogical7  = _g4.LogicalVolume(consSolid7,'G4_Cu','consLogical7')
    consPhysical7 = _g4.PhysicalVolume([0,0,0],[200,-200,0],consLogical7,'consPhysical7',worldLogical)

    consSolid8    = _g4.solid.Cons("cons_solid8", 5, 10, 20, 25, 40, 0, (2)*_np.pi)
    consLogical8  = _g4.LogicalVolume(consSolid8,'G4_Cu','consLogical8')
    consPhysical8 = _g4.PhysicalVolume([0,0,0],[200,0,0],consLogical8,'consPhysical8',worldLogical)

    consSolid9    = _g4.solid.Cons("cons_solid9", 5, 10, 20, 25, 40, 0, (4./3.)*_np.pi)
    consLogical9  = _g4.LogicalVolume(consSolid9,'G4_Cu','consLogical9')
    consPhysical9 = _g4.PhysicalVolume([0,0,0],[200,200,0],consLogical9,'consPhysical9',worldLogical)

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
        w.write('./Cons.gdml')
        w.writeGmadTester('Cons.gmad')        
