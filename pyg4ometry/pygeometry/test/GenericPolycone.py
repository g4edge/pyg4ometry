import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')


    genPolySolid1    = _g4.solid.GenericPolycone("genPolysolid1", 0., 2*_np.pi, 4, 4, [2,4,4,2], [2,2,-2,-2])
    genPolyLogical1  = _g4.LogicalVolume(genPolySolid1,'G4_Cu','genPolyLogical1')
    genPolyPhysical1 = _g4.PhysicalVolume([0,0,0],[0,0,0],genPolyLogical1,'genPolyPhysical1',worldLogical)

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
        w.write('./GenericPolycone.gdml')
        w.writeGmadTester('GenericPolycone.gmad')
