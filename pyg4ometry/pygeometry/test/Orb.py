import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    orbSolid1    = _g4.solid.Orb('orb1',80)
    orbLogical1  = _g4.LogicalVolume(orbSolid1,'G4_Cu','orbLogical1')
    orbPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], orbLogical1,'orbPhysical1',worldLogical)

    orbSolid2    = _g4.solid.Orb('orb2',20)
    orbLogical2  = _g4.LogicalVolume(orbSolid2,'G4_Cu','orbLogical2')
    orbPhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], orbLogical2,'orbPhysical2',worldLogical)

    orbSolid3    = _g4.solid.Orb('orb3',100)
    orbLogical3  = _g4.LogicalVolume(orbSolid3,'G4_Cu','orbLogical3')
    orbPhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], orbLogical3,'orbPhysical3',worldLogical)

    orbSolid4    = _g4.solid.Orb('orb4',60)
    orbLogical4  = _g4.LogicalVolume(orbSolid1,'G4_Cu','orbLogical4')
    orbPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], orbLogical4,'orbPhysical4',worldLogical)



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
        w.write('./Orb.gdml')
        w.writeGmadTester('Orb.gmad')        
