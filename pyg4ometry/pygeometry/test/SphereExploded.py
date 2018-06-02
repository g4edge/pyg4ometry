import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np
import cProfile as _cp
import gc as _gc

# sb mac profile 14.657, 15.325, 15.522, 15.253, 15.020 (Sphere.csgmesh)

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True, stlWriter = True) :
    _g4.registry.clear()

    worldSolid      = _g4.solid.Box('worldBox',500,500,500)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    sphereSolid1    = _g4.solid.Sphere('sphere1',30,50,0,_np.pi*2,0.85*_np.pi,0.15*_np.pi)
    sphereLogical1  = _g4.LogicalVolume(sphereSolid1,'G4_Cu','sphereLogical3')
    spherePhysical1 = _g4.PhysicalVolume([0,0,0],[0,0,0],sphereLogical1,'spherePhysical1',worldLogical)    

    sphereSolid2    = _g4.solid.Sphere('sphere2',30,50,0,2*_np.pi,2.*_np.pi/3.,11*_np.pi/60.)
    sphereLogical2  = _g4.LogicalVolume(sphereSolid2,'G4_Cu','sphereLogical2')
    spherePhysical2 = _g4.PhysicalVolume([0,0,0],[0,0,50],sphereLogical2,'spherePhysical2',worldLogical)

    sphereSolid3    = _g4.solid.Sphere('sphere3',30,50,0,_np.pi*2,_np.pi/3.,_np.pi/3.)
    sphereLogical3  = _g4.LogicalVolume(sphereSolid3,'G4_Cu','sphereLogical3')
    spherePhysical3 = _g4.PhysicalVolume([0,0,0],[0,0,100],sphereLogical3,'spherePhysical3',worldLogical)

    sphereSolid4    = _g4.solid.Sphere('sphere4',30,50,0,_np.pi*2,0.15*_np.pi,11*_np.pi/60.)
    sphereLogical4  = _g4.LogicalVolume(sphereSolid4,'G4_Cu','sphereLogical4')
    spherePhysical4 = _g4.PhysicalVolume([0,0,0],[0,0,150],sphereLogical4,'spherePhysical4',worldLogical)

    sphereSolid5    = _g4.solid.Sphere('sphere5',30,50,0,_np.pi*2,0, 0.15*_np.pi)
    sphereLogical5  = _g4.LogicalVolume(sphereSolid5,'G4_Cu','sphereLogical5')
    spherePhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,200],sphereLogical5,'spherePhysical5',worldLogical)

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
        w.write('./SphereExploded.gdml')
        w.writeGmadTester('SphereExploded.gmad')


    if stlWriter:
        vtkConverter = _vtk.Convert()
        vtkPD = vtkConverter.MeshListToPolyData(m)
        print vtkPD
        _vtk.WriteSTL("./SphereExploded.stl", vtkPD)
