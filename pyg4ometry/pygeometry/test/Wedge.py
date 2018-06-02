import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    wedgeSolid1    = _g4.solid.Wedge('wedge1',25,0,1.5,10)
    wedgeLogical1  = _g4.LogicalVolume(wedgeSolid1,'G4_Cu','wedgeLogical1')
    wedgePhysical1 = _g4.PhysicalVolume([0,0,0],[70,70,0], wedgeLogical1,'wedgePhysical1',worldLogical)

    wedgeSolid2    = _g4.solid.Wedge('wedge2',20,0,_np.pi,15)
    wedgeLogical2  = _g4.LogicalVolume(wedgeSolid2,'G4_Cu','wedgeLogical2')
    wedgePhysical2 = _g4.PhysicalVolume([0,0,0],[70,0,0], wedgeLogical2,'wedgePhysical2',worldLogical)

    wedgeSolid3    = _g4.solid.Wedge('wedge3',35,1.5,4.5,10)
    wedgeLogical3  = _g4.LogicalVolume(wedgeSolid3,'G4_Cu','wedgeLogical3')
    wedgePhysical3 = _g4.PhysicalVolume([0,0,0],[0,70,0], wedgeLogical3,'wedgePhysical3',worldLogical)
    

    wedgeSolid4    = _g4.solid.Wedge('wedge4',15,0,3.*_np.pi/2.,8)
    wedgeLogical4  = _g4.LogicalVolume(wedgeSolid4,'G4_Cu','wedgeLogical4')
    wedgePhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], wedgeLogical4,'wedgePhysical4',worldLogical)
    
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
        w.write('./Wedge.gdml')
        w.writeGmadTester('Wedge.gmad')
