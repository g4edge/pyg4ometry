import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    paraSolid1    = _g4.solid.Para('para1',30,40,60,0.2,0.2,0.2)
    paraLogical1  = _g4.LogicalVolume(paraSolid1,'G4_Cu','paraLogical1')
    paraPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], paraLogical1,'paraPhysical1',worldLogical)

    paraSolid2    = _g4.solid.Para('para2',35,45,65,0.3,0.1,0.)
    paraLogical2  = _g4.LogicalVolume(paraSolid2,'G4_Cu','paraLogical2')
    paraPhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], paraLogical2,'paraPhysical2',worldLogical)

    paraSolid3    = _g4.solid.Para('para3',30,50,60,.2,.2,.1)
    paraLogical3  = _g4.LogicalVolume(paraSolid1,'G4_Cu','paraLogical3')
    paraPhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], paraLogical3,'paraPhysical3',worldLogical)

    paraSolid4    = _g4.solid.Para('para4',25,50,60,0.1,0.1,0.0)
    paraLogical4  = _g4.LogicalVolume(paraSolid4,'G4_Cu','paraLogical4')
    paraPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], paraLogical4,'paraPhysical4',worldLogical)

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
        w.write('./Para.gdml')
        w.writeGmadTester('Para.gmad')        
