import pygeometry.geant4 as _g4
import pygeometry.vtk    as _vtk
import pygeometry.gdml   as _gdml
import numpy             as _np

def PhysicalVolume() : 
    w  = _g4.solid.Box('wbox',500,500,500)
    lw = _g4.LogicalVolume(w,'G4_Galactic','wor') 
    
    s1 = _g4.solid.Box('box',50,50,50)
    lv = _g4.LogicalVolume(s1,'G4_Galactic','log')

    vup = _g4.Parameter("vup",[0,0,250])
    
    pv = _g4.PhysicalVolume([0,0,0],[0,0,150],lv,'ppv1',lw)
    pv = _g4.PhysicalVolume([0,0,_np.pi/8],[0,0,0],lv,'ppv2',lw)
    pv = _g4.PhysicalVolume([0,0,_np.pi/4],[0,0,-150],lv,'ppv3',lw)

    s2  = _g4.solid.Box('box1',10,10,10)
    slv = _g4.LogicalVolume(s2,'G4_Galactic','slog')
    pv1 = _g4.PhysicalVolume([0,0,0],[0,-50,0] ,slv,'pv1',lv,[1,1,1])
    pv2 = _g4.PhysicalVolume([_np.pi/8,0,0],[0,0,0]  ,slv,'pv2',lv,[1,1,1])
    pv3 = _g4.PhysicalVolume([_np.pi/4,0,0],[0, 50,0],slv,'pv3',lv,[1,1,1])

    # clip the world logical volume
    lw.setClip();

    # register the world volume
    _g4.registry.setWorld('wor')

    # display 
    m = lw.pycsgmesh()    
    v = _vtk.Viewer()
    v.addPycsgMeshList(m)
    v.view()

    # write gdml
    w = _gdml.Writer()
    w.addDetector(_g4.registry)
    w.write('./Volume.gdml')
    
