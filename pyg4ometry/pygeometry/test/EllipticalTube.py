import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    ellipticaltubeSolid1    = _g4.solid.EllipticalTube('ellipticaltube1',5,10,20)
    ellipticaltubeLogical1  = _g4.LogicalVolume(ellipticaltubeSolid1,'G4_Cu','ellipticaltubeLogical1')
    ellipticaltubePhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], ellipticaltubeLogical1,'ellipticaltubePhysical1',worldLogical)

    ellipticaltubeSolid2    = _g4.solid.EllipticalTube('ellipticaltube2',10,30,50)
    ellipticaltubeLogical2  = _g4.LogicalVolume(ellipticaltubeSolid2,'G4_Cu','ellipticaltubeLogical2')
    ellipticaltubePhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], ellipticaltubeLogical2,'ellipticaltubePhysical2',worldLogical)

    ellipticaltubeSolid3    = _g4.solid.EllipticalTube('ellipticaltube3',30,50,20)
    ellipticaltubeLogical3  = _g4.LogicalVolume(ellipticaltubeSolid3,'G4_Cu','ellipticaltubeLogical3')
    ellipticaltubePhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], ellipticaltubeLogical3,'ellipticaltubePhysical3',worldLogical)

    ellipticaltubeSolid4    = _g4.solid.EllipticalTube('ellipticaltube4',10,20,40)
    ellipticaltubeLogical4  = _g4.LogicalVolume(ellipticaltubeSolid4,'G4_Cu','ellipticaltubeLogical4')
    ellipticaltubePhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], ellipticaltubeLogical4,'ellipticaltubePhysical4',worldLogical)
    
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
        w.write('./EllipticalTube.gdml')
        w.writeGmadTester('EllipticalTube.gmad')        
