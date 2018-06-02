import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    polyhedraSolid1    = _g4.solid.Polyhedra("polyhedra_solid1",
                                             0*_np.pi/4., 2*_np.pi, 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical1  = _g4.LogicalVolume(polyhedraSolid1,'G4_Cu','polyhedraLogical1')
    polyhedraPhysical1 = _g4.PhysicalVolume([0,0,0],[-200,-200,0],polyhedraLogical1,'polyhedraPhysical1',worldLogical)
    
    

    polyhedraSolid2    = _g4.solid.Polyhedra("polyhedra_solid2",
                                             0, 2*_np.pi/3., 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical2  = _g4.LogicalVolume(polyhedraSolid2,'G4_Cu','polyhedraLogical2')
    polyhedraPhysical2 = _g4.PhysicalVolume([0,0,0],[-200,0,0],polyhedraLogical2,'polyhedraPhysical2',worldLogical)
    

    
    polyhedraSolid3    = _g4.solid.Polyhedra("polyhedra_solid3",
                                             0, _np.pi, 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical3  = _g4.LogicalVolume(polyhedraSolid3,'G4_Cu','polyhedraLogical3')
    polyhedraPhysical3 = _g4.PhysicalVolume([0,0,0],[-200,200,0],polyhedraLogical3,'polyhedraPhysical3',worldLogical)

    

    polyhedraSolid4    = _g4.solid.Polyhedra("polyhedra_solid4",
                                             0, _np.pi/4, 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical4  = _g4.LogicalVolume(polyhedraSolid4,'G4_Cu','polyhedraLogical4')
    polyhedraPhysical4 = _g4.PhysicalVolume([0,0,0],[0,-200,0],polyhedraLogical4,'polyhedraPhysical4',worldLogical)

    

    polyhedraSolid5    = _g4.solid.Polyhedra("polyhedra_solid5",
                                             0, 3*_np.pi/2., 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical5  = _g4.LogicalVolume(polyhedraSolid5,'G4_Cu','polyhedraLogical5')
    polyhedraPhysical5 = _g4.PhysicalVolume([0,0,0],[0,0,0],polyhedraLogical5,'polyhedraPhysical5',worldLogical)

    
    
    polyhedraSolid6    = _g4.solid.Polyhedra("polyhedra_solid6",
                                             0, _np.pi/2., 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical6  = _g4.LogicalVolume(polyhedraSolid6,'G4_Cu','polyhedraLogical6')
    polyhedraPhysical6 = _g4.PhysicalVolume([0,0,0],[0,200,0],polyhedraLogical6,'polyhedraPhysical6',worldLogical)


    
    polyhedraSolid7    = _g4.solid.Polyhedra("polyhedra_solid7",
                                             0, 2*_np.pi, 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical7  = _g4.LogicalVolume(polyhedraSolid7,'G4_Cu','polyhedraLogical7')
    polyhedraPhysical7 = _g4.PhysicalVolume([0,0,0],[200,-200,0],polyhedraLogical7,'polyhedraPhysical7',worldLogical)


    
    polyhedraSolid8    = _g4.solid.Polyhedra("polyhedra_solid8",
                                             0, 5*_np.pi/3., 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical8  = _g4.LogicalVolume(polyhedraSolid8,'G4_Cu','polyhedraLogical8')
    polyhedraPhysical8 = _g4.PhysicalVolume([0,0,0],[200,0,0],polyhedraLogical8,'polyhedraPhysical8',worldLogical)


    
    polyhedraSolid9    = _g4.solid.Polyhedra("polyhedra_solid9",
                                             0*_np.pi/4., 2*_np.pi, 5, 7,
                                             [0, 5*5,5*8,5*13,5*30,5*32,5*35],
                                             [0,0,0,0,0,0,0,0,0],
                                             [0,5*15,5*15,5*4,5*4,5*10,5*10])
    polyhedraLogical9  = _g4.LogicalVolume(polyhedraSolid9,'G4_Cu','polyhedraLogical9')
    polyhedraPhysical9 = _g4.PhysicalVolume([0,0,0],[200,200,0],polyhedraLogical9,'polyhedraPhysical9',worldLogical)

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
        w.write('./Polyhedra.gdml')
        w.writeGmadTester('Polyhedra.gmad')        
