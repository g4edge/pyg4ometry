import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np
import cProfile as _cp
import gc as _gc

# sb mac profile 14.657, 15.325, 15.522, 15.253, 15.020 (Sphere.csgmesh)

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid      = _g4.solid.Box('worldBox',500,500,500)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    sphereSolid1    = _g4.solid.Sphere('sphere1',0,50,0,_np.pi*2,0,_np.pi)
    sphereLogical1  = _g4.LogicalVolume(sphereSolid1,'G4_Cu','sphereLogical1')
    spherePhysical1 = _g4.PhysicalVolume([0,0,0],[0,0,0],sphereLogical1,'spherePhysical1',worldLogical)

    sphereSolid2    = _g4.solid.Sphere('sphere2',30,40,0,_np.pi*2,0,_np.pi)
    sphereLogical2  = _g4.LogicalVolume(sphereSolid2,'G4_Cu','sphereLogical2')
    spherePhysical2 = _g4.PhysicalVolume([0,0,0],[200,0,0],sphereLogical2,'spherePhysical2',worldLogical)

    sphereSolid3    = _g4.solid.Sphere('sphere3',0,50,0,_np.pi*2,0,_np.pi/2.)
    sphereLogical3  = _g4.LogicalVolume(sphereSolid3,'G4_Cu','sphereLogical3')
    spherePhysical3 = _g4.PhysicalVolume([0,0,0],[200,200,0],sphereLogical3,'spherePhysical3',worldLogical)

    sphereSolid4    = _g4.solid.Sphere('sphere4',30,50,0,_np.pi*2,0,_np.pi/2.)
    sphereLogical4  = _g4.LogicalVolume(sphereSolid4,'G4_Cu','sphereLogical4')
    spherePhysical4 = _g4.PhysicalVolume([0,0,0],[0,200,0],sphereLogical4,'spherePhysical4',worldLogical)

    sphereSolid5    = _g4.solid.Sphere('sphere5',0,50,0,_np.pi*2,0,2*_np.pi/3.)
    sphereLogical5  = _g4.LogicalVolume(sphereSolid5,'G4_Cu','sphereLogical5')
    spherePhysical5 = _g4.PhysicalVolume([0,0,0],[0,-200,0],sphereLogical5,'spherePhysical5',worldLogical)

    sphereSolid6    = _g4.solid.Sphere('sphere6',0,50,0,_np.pi*2,2*_np.pi/3.,_np.pi/3.)
    sphereLogical6  = _g4.LogicalVolume(sphereSolid6,'G4_Cu','sphereLogical6')
    spherePhysical6 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],sphereLogical6,'spherePhysical6',worldLogical)

    sphereSolid7    = _g4.solid.Sphere('sphere7',0,50,0,_np.pi*2,2*_np.pi/3.,11*_np.pi/60.)
    sphereLogical7  = _g4.LogicalVolume(sphereSolid7,'G4_Cu','sphereLogical7')
    spherePhysical7 = _g4.PhysicalVolume([0,0,0],[-200,200,0],sphereLogical7,'spherePhysical7',worldLogical)
    
    sphereSolid8    = _g4.solid.Sphere('sphere8',0,50,0,_np.pi*2,0.85*_np.pi, 3*_np.pi/20.)
    sphereLogical8  = _g4.LogicalVolume(sphereSolid8,'G4_Cu','sphereLogical8')
    spherePhysical8 = _g4.PhysicalVolume([0,0,0],[-200,0,0],sphereLogical8,'spherePhysical8',worldLogical)

    sphereSolid9    = _g4.solid.Sphere('sphere9',0,50,0,_np.pi*2,_np.pi/4., _np.pi/12.)
    sphereLogical9  = _g4.LogicalVolume(sphereSolid9,'G4_Cu','sphereLogical9')
    spherePhysical9 = _g4.PhysicalVolume([0,0,0],[200,-200,0],sphereLogical9,'spherePhysical9',worldLogical)

    sphereSolid10    = _g4.solid.Sphere('sphere10',0,50,0,_np.pi/2.,0, _np.pi)
    sphereLogical10  = _g4.LogicalVolume(sphereSolid10,'G4_Cu','sphereLogical10')
    spherePhysical10 = _g4.PhysicalVolume([0,0,0],[400,0,0],sphereLogical10,'spherePhysical10',worldLogical)

    sphereSolid11    = _g4.solid.Sphere('sphere11',0,50,0,2.*_np.pi/3.,0, _np.pi)
    sphereLogical11  = _g4.LogicalVolume(sphereSolid11,'G4_Cu','sphereLogical11')
    spherePhysical11 = _g4.PhysicalVolume([0,0,0],[400,-200,0],sphereLogical11,'spherePhysical11',worldLogical)

    sphereSolid12    = _g4.solid.Sphere('sphere12',30,50,0,4.*_np.pi/3.,0, 2.*_np.pi/3.)
    sphereLogical12  = _g4.LogicalVolume(sphereSolid12,'G4_Cu','sphereLogical12')
    spherePhysical12 = _g4.PhysicalVolume([0,0,0],[400,200,0],sphereLogical12,'spherePhysical12',worldLogical)

    
    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')
    
    m = worldLogical.pycsgmesh()
    print m
    
    if vtkViewer : 
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();

    # write gdml
    if gdmlWriter : 
        w = _gdml.Writer()
        w.addDetector(_g4.registry)
        w.write('./SphereFullTest.gdml')
        w.writeGmadTester('SphereFullTest.gmad')        

