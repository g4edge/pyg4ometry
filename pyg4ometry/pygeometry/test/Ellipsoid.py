import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    ellipsoidSolid1    = _g4.solid.Ellipsoid("ellipsoid_solid1", 40., 60., 100., -100., 100.)
    ellipsoidLogical1  = _g4.LogicalVolume(ellipsoidSolid1,'G4_Cu','ellipsoidLogical1')
    ellipsoidPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],ellipsoidLogical1,'ellipsoidPhysical1',worldLogical)
    
    ellipsoidSolid2    = _g4.solid.Ellipsoid("ellipsoid_solid2", 40., 40., 40., -40., 40.)
    ellipsoidLogical2  = _g4.LogicalVolume(ellipsoidSolid2,'G4_Cu','ellipsoidLogical2')
    ellipsoidPhysical2 = _g4.PhysicalVolume([0,0,0],[-200,0,0],ellipsoidLogical2,'ellipsoidPhysical2',worldLogical)
    
    ellipsoidSolid3    = _g4.solid.Ellipsoid("ellipsoid_solid3", 50., 50., 30., -30., 30.)
    ellipsoidLogical3  = _g4.LogicalVolume(ellipsoidSolid3,'G4_Cu','ellipsoidLogical3')
    ellipsoidPhysical3 = _g4.PhysicalVolume([0,0,0],[-200,200,0],ellipsoidLogical3,'ellipsoidPhysical3',worldLogical)
    
    ellipsoidSolid4    = _g4.solid.Ellipsoid("ellipsoid_solid4", 40., 60., 100., -70., 70.)
    ellipsoidLogical4  = _g4.LogicalVolume(ellipsoidSolid4,'G4_Cu','ellipsoidLogical4')
    ellipsoidPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-200,0],ellipsoidLogical4,'ellipsoidPhysical4',worldLogical)

    ellipsoidSolid5    = _g4.solid.Ellipsoid("ellipsoid_solid5", 40., 60., 100., -20., 80.)
    ellipsoidLogical5  = _g4.LogicalVolume(ellipsoidSolid5,'G4_Cu','ellipsoidLogical5')
    ellipsoidPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],ellipsoidLogical5,'ellipsoidPhysical5',worldLogical)
    
    ellipsoidSolid6    = _g4.solid.Ellipsoid("ellipsoid_solid6", 40., 60., 100., -15., 15.)
    ellipsoidLogical6  = _g4.LogicalVolume(ellipsoidSolid6,'G4_Cu','ellipsoidLogical6')
    ellipsoidPhysical6 = _g4.PhysicalVolume([0,0,0],[0,200,0],ellipsoidLogical6,'ellipsoidPhysical6',worldLogical)

    ellipsoidSolid7    = _g4.solid.Ellipsoid("ellipsoid_solid7", 40., 60., 100., 50, 100.)
    ellipsoidLogical7  = _g4.LogicalVolume(ellipsoidSolid7,'G4_Cu','ellipsoidLogical7')
    ellipsoidPhysical7 = _g4.PhysicalVolume([0,0,0],[200,-200,0],ellipsoidLogical7,'ellipsoidPhysical7',worldLogical)

    ellipsoidSolid8    = _g4.solid.Ellipsoid("ellipsoid_solid8", 40., 60., 100., -100., -50.)
    ellipsoidLogical8  = _g4.LogicalVolume(ellipsoidSolid8,'G4_Cu','ellipsoidLogical8')
    ellipsoidPhysical8 = _g4.PhysicalVolume([0,0,0],[200,0,0],ellipsoidLogical8,'ellipsoidPhysical8',worldLogical)

    ellipsoidSolid9    = _g4.solid.Ellipsoid("ellipsoid_solid9", 40., 60., 100., -50., 50.)
    ellipsoidLogical9  = _g4.LogicalVolume(ellipsoidSolid9,'G4_Cu','ellipsoidLogical9')
    ellipsoidPhysical9 = _g4.PhysicalVolume([0,0,0],[200,200,0],ellipsoidLogical9,'ellipsoidPhysical9',worldLogical)

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
        w.write('./Ellipsoid.gdml')
        w.writeGmadTester('Ellipsoid.gmad')        
