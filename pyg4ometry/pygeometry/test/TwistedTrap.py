import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    twistedTrapSolid1    = _g4.solid.TwistedTrap('twistedTrap1',-0.5,60,0.3,0.08,40,30,40,16,10,14,0.16)
    twistedTrapLogical1  = _g4.LogicalVolume(twistedTrapSolid1,'G4_Cu','twistedTrapLogical1')
    twistedTrapPhysical1 = _g4.PhysicalVolume([0,0,0],[0,0,0], twistedTrapLogical1,'twistedTrapPhysical1',worldLogical)

    twistedTrapSolid2    = _g4.solid.TwistedTrap('twistedTrap2',0.5,60,0,0,40,30,40,16,10,14,0)
    twistedTrapLogical2  = _g4.LogicalVolume(twistedTrapSolid2,'G4_Cu','twistedTrapLogical2')
    twistedTrapPhysical2 = _g4.PhysicalVolume([0,0,0],[200,200,0], twistedTrapLogical2,'twistedTrapPhysical2',worldLogical)
    
    
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
        w.write('./TwistedTrap.gdml')
        w.writeGmadTester('TwistedTrap.gmad')        
