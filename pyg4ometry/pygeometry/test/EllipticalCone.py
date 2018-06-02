import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    ellipticalconeSolid1    = _g4.solid.EllipticalCone('ellipticalcone1',0.4,0.8,50,25)
    ellipticalconeLogical1  = _g4.LogicalVolume(ellipticalconeSolid1,'G4_Cu','ellipticalconeLogical1')
    ellipticalconePhysical1 = _g4.PhysicalVolume([0,0,0],[-200,200,0], ellipticalconeLogical1,'ellipticalconePhysical1',worldLogical)

    ellipticalconeSolid2    = _g4.solid.EllipticalCone('ellipticalcone2',0.2, 0.4,60,30)
    ellipticalconeLogical2  = _g4.LogicalVolume(ellipticalconeSolid2,'G4_Cu','ellipticalconeLogical2')
    ellipticalconePhysical2 = _g4.PhysicalVolume([0,0,0],[0,200,0], ellipticalconeLogical2,'ellipticalconePhysical2',worldLogical)

    ellipticalconeSolid3    = _g4.solid.EllipticalCone('ellipticalcone3',.3, 0.6,40,20)
    ellipticalconeLogical3  = _g4.LogicalVolume(ellipticalconeSolid3,'G4_Cu','ellipticalconeLogical3')
    ellipticalconePhysical3 = _g4.PhysicalVolume([0,0,0],[200,200,0], ellipticalconeLogical3,'ellipticalconePhysical3',worldLogical)

    ellipticalconeSolid4    = _g4.solid.EllipticalCone('ellipticalcone4',.4, .9,30.0,.70)
    ellipticalconeLogical4  = _g4.LogicalVolume(ellipticalconeSolid4,'G4_Cu','ellipticalconeLogical4')
    ellipticalconePhysical4 = _g4.PhysicalVolume([0,0,0],[-200,0,0], ellipticalconeLogical4,'ellipticalconePhysical4',worldLogical)

    ellipticalconeSolid5    = _g4.solid.EllipticalCone('ellipticalcone5',0.2, 0.6,30.0,17.0)
    ellipticalconeLogical5  = _g4.LogicalVolume(ellipticalconeSolid5,'G4_Cu','ellipticalconeLogical5')
    ellipticalconePhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0], ellipticalconeLogical5,'ellipticalconePhysical5',worldLogical)

    ellipticalconeSolid6    = _g4.solid.EllipticalCone('ellipticalcone6',1, 1.5,30.0,15.0)
    ellipticalconeLogical6  = _g4.LogicalVolume(ellipticalconeSolid6,'G4_Cu','ellipticalconeLogical6')
    ellipticalconePhysical6 = _g4.PhysicalVolume([0,0,0],[200,0,0], ellipticalconeLogical6,'ellipticalconePhysical6',worldLogical)

    ellipticalconeSolid7    = _g4.solid.EllipticalCone('ellipticalcone7',1.5, 1.6,40.0,25.0)
    ellipticalconeLogical7  = _g4.LogicalVolume(ellipticalconeSolid7,'G4_Cu','ellipticalconeLogical7')
    ellipticalconePhysical7 = _g4.PhysicalVolume([0,0,0],[-200,-200,0], ellipticalconeLogical7,'ellipticalconePhysical7',worldLogical)

    ellipticalconeSolid8    = _g4.solid.EllipticalCone('ellipticalcone8',0.85, 0.64,30.0,10.0)
    ellipticalconeLogical8  = _g4.LogicalVolume(ellipticalconeSolid8,'G4_Cu','ellipticalconeLogical8')
    ellipticalconePhysical8 = _g4.PhysicalVolume([0,0,0],[0,-200,0], ellipticalconeLogical8,'ellipticalconePhysical8',worldLogical)

    ellipticalconeSolid9    = _g4.solid.EllipticalCone('ellipticalcone9',.8, 0.3,30.0,15.0)
    ellipticalconeLogical9  = _g4.LogicalVolume(ellipticalconeSolid9,'G4_Cu','ellipticalconeLogical9')
    ellipticalconePhysical9 = _g4.PhysicalVolume([0,0,0],[200,-200,0], ellipticalconeLogical9,'ellipticalconePhysical9',worldLogical)

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
        w.write('./EllipticalCone.gdml')
        w.writeGmadTester('EllipticalCone.gmad')        
