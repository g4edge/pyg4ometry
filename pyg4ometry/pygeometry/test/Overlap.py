import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import warnings as _warnings
from matplotlib.cbook import flatten


def visualise_overlaps(meshlist,  worldVolumeIncluded=True):
    m = meshlist #shortcut

    #Check for overlaps
    mo = _g4.pycsg_overlap(m, worldVolumeIncluded=worldVolumeIncluded)

    # change view setttings of meshes
    mfl = [] # flat mesh list
    for me in flatten(m) :
        me.alpha = 0.25
        mfl.append(me)

    # change view setttings of overlapping meshes
    moc = [] # flat mesh list
    for me in flatten(mo) :
        me.colour = (0,0,255)
        moc.append(me)

    # view the geometry
    v = _vtk.Viewer()
    v.addPycsgMeshList(mfl)
    v.addPycsgMeshList(moc)
    v.view();


def pycsgmeshTest(vtkViewer = True, gdmlWriter = True) :
    _g4.registry.clear()

    worldSolid      = _g4.solid.Box('worldBox',250,250,100)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    box1_solid   = _g4.solid.Box("b1", 10, 10, 10)
    box1_logical = _g4.LogicalVolume(box1_solid,'G4_Cu','box1_logical')
    box1_volume  = _g4.PhysicalVolume([0,0,0], [0, 0, 0], box1_logical,  "box1_physical", worldLogical)

    box2_solid   = _g4.solid.Box("b2", 10, 10, 10)
    box2_logical = _g4.LogicalVolume(box2_solid,'G4_Cu','box2_logical')
    box2_volume  = _g4.PhysicalVolume([0,0,0.785], [0, 0, 7.5], box2_logical,  "box2_physical", worldLogical)


    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')

    # mesh the geometry
    m = worldLogical.pycsgmesh()

    if vtkViewer:
        visualise_overlaps(m, True)

    if gdmlWriter:
        warnings.warn("GDML file writing not supported for overlap test! No file produced, contunie...")



