import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')
    
    hypeSolid1    = _g4.solid.Hype('hype1',20,30,0.7,0.7,50)
    hypeLogical1  = _g4.LogicalVolume(hypeSolid1,'G4_Cu','hypeLogical1')
    hypePhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], hypeLogical1,'hypePhysical1',worldLogical)

    hypeSolid2    = _g4.solid.Hype('hype2',15,40,0.75,0.7,60)
    hypeLogical2  = _g4.LogicalVolume(hypeSolid2,'G4_Cu','hypeLogical2')
    hypePhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], hypeLogical2,'hypePhysical2',worldLogical)

    hypeSolid3    = _g4.solid.Hype('hype3',20,25,0.7,0.7,45)
    hypeLogical3  = _g4.LogicalVolume(hypeSolid3,'G4_Cu','hypeLogical3')
    hypePhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], hypeLogical3,'hypePhysical3',worldLogical)

    hypeSolid4    = _g4.solid.Hype('hype4',15,30,0.65,0.65,40)
    hypeLogical4  = _g4.LogicalVolume(hypeSolid4,'G4_Cu','hypeLogical4')
    hypePhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], hypeLogical4,'hypePhysical4',worldLogical)
    
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
        w.write('./Hype.gdml')
        w.writeGmadTester('Hype.gmad')        
