import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 500,500,150)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    twistedBoxSolid1    = _g4.solid.TwistedBox('twistedBox1',0.5, 30, 40, 60)
    twistedBoxLogical1  = _g4.LogicalVolume(twistedBoxSolid1,'G4_Cu','twistedBoxLogical1')
    twistedBoxPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], twistedBoxLogical1,'twistedBoxPhysical1',worldLogical)

    twistedBoxSolid2    = _g4.solid.TwistedBox('twistedBox2',0.2, 50, 40, 60)
    twistedBoxLogical2  = _g4.LogicalVolume(twistedBoxSolid2,'G4_Cu','twistedBoxLogical2')
    twistedBoxPhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], twistedBoxLogical2,'twistedBoxPhysical2',worldLogical)

    twistedBoxSolid3    = _g4.solid.TwistedBox('twistedBox3',1.5, 20, 30, 40)
    twistedBoxLogical3  = _g4.LogicalVolume(twistedBoxSolid3,'G4_Cu','twistedBoxLogical3')
    twistedBoxPhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], twistedBoxLogical3,'twistedBoxPhysical3',worldLogical)

    twistedBoxSolid4    = _g4.solid.TwistedBox('twistedBox4',0.5, 30, 40, 50)
    twistedBoxLogical4  = _g4.LogicalVolume(twistedBoxSolid4,'G4_Cu','twistedBoxLogical4')
    twistedBoxPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], twistedBoxLogical4,'twistedBoxPhysical4',worldLogical)

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
        w.write('./TwistedBox.gdml')
        w.writeGmadTester('TwistedBox.gmad')        
