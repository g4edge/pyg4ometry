import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid   = _g4.solid.Box('worldBox', 250,250,100)
    worldLogical =  _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    trapSolid1    = _g4.solid.Trap('trap1',
                                   25,
                                   1, 2,
                                   37.5, 25, 25,
                                   1,
                                   37.5, 25, 25,
                                   1)
    
    trapLogical1  = _g4.LogicalVolume(trapSolid1,'G4_Cu','trapLogical1')
    trapPhysical1 = _g4.PhysicalVolume([0,0,0],[200,200,0], trapLogical1,'trapPhysical1',worldLogical)

    
    trapSolid2    = _g4.solid.Trap('trap2',
                                   60,
                                   _np.pi/9., 5*_np.pi/180.,
                                   40, 30, 40,
                                   _np.pi/18.,
                                   16, 10, 14,
                                   _np.pi/18.)
    
    trapLogical2  = _g4.LogicalVolume(trapSolid2,'G4_Cu','trapLogical2')
    trapPhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0], trapLogical2,'trapPhysical2',worldLogical)


    trapSolid3    = _g4.solid.Trap('trap3',
                                   60,
                                   _np.pi/9., 5*_np.pi/180.,
                                   40, 30, 40,
                                   _np.pi/18.,
                                   16, 10, 14,
                                   _np.pi/18.)
    
    trapLogical3  = _g4.LogicalVolume(trapSolid3,'G4_Cu','trapLogical3')
    trapPhysical3 = _g4.PhysicalVolume([0,0,0],[0,200,0], trapLogical3,'trapPhysical3',worldLogical)

    trapSolid4    = _g4.solid.Trap('trap4',
                                   60,
                                   _np.pi/9., 5*_np.pi/180.,
                                   40, 30, 40,
                                   _np.pi/18.,
                                   16, 10, 14,
                                   _np.pi/18.)
    
    trapLogical4  = _g4.LogicalVolume(trapSolid4,'G4_Cu','trapLogical4')
    trapPhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,0], trapLogical4,'trapPhysical4',worldLogical)
    
    
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
        w.write('./Trap.gdml')
        w.writeGmadTester('Trap.gmad')        
