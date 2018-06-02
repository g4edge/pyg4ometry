import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    bsize        = _g4.Parameter("BOXSIZE",25)
    boffset      = _g4.Parameter("BOXOFFSET",200)
    zero         = _g4.Parameter("ZERO",0)

    boxSolid1    = _g4.solid.Box('box1',2*bsize,2*bsize,2*bsize)
    boxLogical1  = _g4.LogicalVolume(boxSolid1,'G4_Cu','boxLogical1')
    boxPosition1 = _g4.ParameterVector("boxPosition1",[-boffset,-boffset,zero])
    boxPhysical1 = _g4.PhysicalVolume([0,0,0],boxPosition1,boxLogical1,'boxPhysical1',worldLogical)

    boxSolid2    = _g4.solid.Box('box2',bsize,bsize,3*bsize)
    boxLogical2  = _g4.LogicalVolume(boxSolid2,'G4_Cu','boxLogical2')
    boxPosition2 = _g4.ParameterVector("boxPosition2",[-boffset,zero,zero])
    boxPhysical2 = _g4.PhysicalVolume([0,0,0],boxPosition2,boxLogical2,'boxPhysical2',worldLogical)

    boxSolid3    = _g4.solid.Box('box3',bsize,3*bsize,bsize)
    boxLogical3  = _g4.LogicalVolume(boxSolid3,'G4_Cu','boxLogical3')
    boxPosition3 = _g4.ParameterVector("boxPosition3",[-boffset,boffset,zero])
    boxPhysical3 = _g4.PhysicalVolume([0,0,0],boxPosition3,boxLogical3,'boxPhysical3',worldLogical)

    boxSolid4    = _g4.solid.Box('box4',3*bsize,bsize,bsize)
    boxLogical4  = _g4.LogicalVolume(boxSolid4,'G4_Cu','boxLogical4')
    boxPosition4 = _g4.ParameterVector("boxPosition4",[zero,-boffset,zero])
    boxPhysical4 = _g4.PhysicalVolume([0,0,0],boxPosition4,boxLogical4,'boxPhysical4',worldLogical)

    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')

    # mesh the geometry
    m = worldLogical.pycsgmesh()

    # view the geometry
    if vtkViewer : 
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();

    # write gdml
    if gdmlWriter : 
        w = _gdml.Writer()
        w.addDetector(_g4.registry)
        w.write('./Box.gdml')
        w.writeGmadTester('Box.gmad')        
