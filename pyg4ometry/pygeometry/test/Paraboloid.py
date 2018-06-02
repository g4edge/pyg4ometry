import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    paraboloidSolid1    = _g4.solid.Paraboloid('paraboloid1',20,20,35)
    paraboloidLogical1  = _g4.LogicalVolume(paraboloidSolid1,'G4_Cu','paraboloidLogical1')
    paraboloidPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], paraboloidLogical1,'paraboloidPhysical1',worldLogical)

    paraboloidSolid2    = _g4.solid.Paraboloid('paraboloid2',50,0,35)
    paraboloidLogical2  = _g4.LogicalVolume(paraboloidSolid2,'G4_Cu','paraboloidLogical2')
    paraboloidPhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], paraboloidLogical2,'paraboloidPhysical2',worldLogical)

    paraboloidSolid3    = _g4.solid.Paraboloid('paraboloid3',40,30,50)
    paraboloidLogical3  = _g4.LogicalVolume(paraboloidSolid3,'G4_Cu','paraboloidLogical3')
    paraboloidPhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], paraboloidLogical3,'paraboloidPhysical3',worldLogical)

    paraboloidSolid4    = _g4.solid.Paraboloid('paraboloid4',50,20,60)
    paraboloidLogical4  = _g4.LogicalVolume(paraboloidSolid4,'G4_Cu','paraboloidLogical4')
    paraboloidPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], paraboloidLogical4,'paraboloidPhysical4',worldLogical)

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
        w.write('./Paraboloid.gdml')
        w.writeGmadTester('Paraboloid.gmad')        
