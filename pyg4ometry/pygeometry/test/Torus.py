import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    torusSolid1    = _g4.solid.Torus("torus_solid1", 40., 60., 200., 0., _np.pi/2, nslice=16, nstack=8)
    torusLogical1  = _g4.LogicalVolume(torusSolid1,'G4_Cu','torusLogical1')
    torusPhysical1 = _g4.PhysicalVolume([0,0,0],[-500,-500,0],torusLogical1,'torusPhysical1',worldLogical)

    torusSolid2    = _g4.solid.Torus("torus_solid2", 10., 30., 200., 0., _np.pi, nslice=16, nstack=8)
    torusLogical2  = _g4.LogicalVolume(torusSolid2,'G4_Cu','torusLogical2')
    torusPhysical2 = _g4.PhysicalVolume([0,0,0],[-500,0,0],torusLogical2,'torusPhysical2',worldLogical)

    torusSolid3    = _g4.solid.Torus("torus_solid3", 40., 60., 150., 0., _np.pi*2, nslice=16, nstack=8)
    torusLogical3  = _g4.LogicalVolume(torusSolid3,'G4_Cu','torusLogical3')
    torusPhysical3 = _g4.PhysicalVolume([0,0,0],[-500,500,0],torusLogical3,'torusPhysical3',worldLogical)

    torusSolid4    = _g4.solid.Torus("torus_solid4", 40.,60., 200., _np.pi/4., (_np.pi*3.)/4., nslice=16, nstack=8)
    torusLogical4  = _g4.LogicalVolume(torusSolid4,'G4_Cu','torusLogical4')
    torusPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-500,0],torusLogical4,'torusPhysical4',worldLogical)

    torusSolid5    = _g4.solid.Torus("torus_solid5", 10., 30., 50., 0., _np.pi, nslice=16, nstack=8)
    torusLogical5  = _g4.LogicalVolume(torusSolid5,'G4_Cu','torusLogical5')
    torusPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],torusLogical5,'torusPhysical5',worldLogical)
    
    torusSolid6    = _g4.solid.Torus("torus_solid6", 50., 60., 200., 0., _np.pi*2, nslice=16, nstack=8)
    torusLogical6  = _g4.LogicalVolume(torusSolid6,'G4_Cu','torusLogical6')
    torusPhysical6 = _g4.PhysicalVolume([0,0,0],[0,500,0],torusLogical6,'torusPhysical6',worldLogical)

    torusSolid7    = _g4.solid.Torus("torus_solid7", 10., 30., 170., _np.pi, _np.pi*2, nslice=16, nstack=8)
    torusLogical7  = _g4.LogicalVolume(torusSolid7,'G4_Cu','torusLogical7')
    torusPhysical7 = _g4.PhysicalVolume([0,0,0],[500,-500,0],torusLogical7,'torusPhysical7',worldLogical)

    torusSolid8    = _g4.solid.Torus("torus_solid8", 40., 60., 120., 0., _np.pi/4, nslice=16, nstack=8)
    torusLogical8  = _g4.LogicalVolume(torusSolid8,'G4_Cu','torusLogical8')
    torusPhysical8 = _g4.PhysicalVolume([0,0,0],[500,0,0],torusLogical8,'torusPhysical8',worldLogical)

    torusSolid9    = _g4.solid.Torus("torus_solid9", 30., 60., 180., 0., _np.pi/3., nslice=16, nstack=8)
    torusLogical9  = _g4.LogicalVolume(torusSolid9,'G4_Cu','torusLogical9')
    torusPhysical9 = _g4.PhysicalVolume([0,0,0],[500,500,0],torusLogical9,'torusPhysical9',worldLogical)

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
        w.write('./Torus.gdml')
        w.writeGmadTester('Torus.gmad')        
