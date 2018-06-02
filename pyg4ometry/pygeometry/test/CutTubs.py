import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml
import numpy as _np

# sb mac profile 14.657, 15.325, 15.522, 15.253, 15.020 (Tubs.csgmesh)

def pycsgmeshTest(vtkViewer=True, gdmlWriter=True):
    _g4.registry.clear()

    worldSolid = _g4.solid.Box('worldBox', 250, 250, 100)
    worldLogical = _g4.LogicalVolume(worldSolid, 'G4_Galactic', 'worldLogical')

    cutTubsSolid1 = _g4.solid.CutTubs('cutTubs1', 0, 50, 50, 0, 2 * _np.pi,[0,0,-1],[0,1,1])
    cutTubsLogical1 = _g4.LogicalVolume(cutTubsSolid1, 'G4_Cu', 'cutTubsLogical1')
    cutTubsPhysical1 = _g4.PhysicalVolume([0, 0, 0], [-200, -200, 0], cutTubsLogical1, 'cutTubsPhysical1', worldLogical)

    cutTubsSolid2 = _g4.solid.CutTubs('cutTubs2', 0, 50, 50, 0, 2 * _np.pi,[0,0,-1],[1,0,1])
    cutTubsLogical2 = _g4.LogicalVolume(cutTubsSolid2, 'G4_Cu', 'cutTubsLogical2')
    cutTubsPhysical2 = _g4.PhysicalVolume([0, 0, 0], [-200, 0, 0], cutTubsLogical2, 'cutTubsPhysical2', worldLogical)

    cutTubsSolid3 = _g4.solid.CutTubs('cutTubs3', 0, 50, 50, 0, 2 * _np.pi,[0,0,-1],[1,1,1])
    cutTubsLogical3 = _g4.LogicalVolume(cutTubsSolid3, 'G4_Cu', 'cutTubsLogical3')
    cutTubsPhysical3 = _g4.PhysicalVolume([0, 0, 0], [-200, 200, 0], cutTubsLogical3, 'cutTubsPhysical3', worldLogical)

    cutTubsSolid4 = _g4.solid.CutTubs('cutTubs4', 0, 50, 50, 0, 2 * _np.pi,[0,-1,-1],[0,0,1])
    cutTubsLogical4 = _g4.LogicalVolume(cutTubsSolid4, 'G4_Cu', 'cutTubsLogical4')
    cutTubsPhysical4 = _g4.PhysicalVolume([0, 0, 0], [0, -200, 0], cutTubsLogical4, 'cutTubsPhysical4', worldLogical)

    cutTubsSolid5 = _g4.solid.CutTubs('cutTubs5', 0, 50, 50, 0, 2 * _np.pi,[-1,0,-1],[0,0,1])
    cutTubsLogical5 = _g4.LogicalVolume(cutTubsSolid5, 'G4_Cu', 'cutTubsLogical5')
    cutTubsPhysical5 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], cutTubsLogical5, 'cutTubsPhysical5', worldLogical)

    cutTubsSolid6 = _g4.solid.CutTubs('cutTubs6', 0, 50, 50, 0, 2 * _np.pi,[-1,-1,-1],[0,0,1])
    cutTubsLogical6 = _g4.LogicalVolume(cutTubsSolid6, 'G4_Cu', 'cutTubsLogical6')
    cutTubsPhysical6 = _g4.PhysicalVolume([0, 0, 0], [0, 200, 0], cutTubsLogical6, 'cutTubsPhysical6', worldLogical)

    cutTubsSolid7 = _g4.solid.CutTubs('cutTubs7', 0, 50, 50, 0, 2 * _np.pi,[0,-1,-1],[1,0,1])
    cutTubsLogical7 = _g4.LogicalVolume(cutTubsSolid7, 'G4_Cu', 'cutTubsLogical7')
    cutTubsPhysical7 = _g4.PhysicalVolume([0, 0, 0], [200, -200, 0], cutTubsLogical7, 'cutTubsPhysical7', worldLogical)

    cutTubsSolid8 = _g4.solid.CutTubs('cutTubs8', 0, 50, 50, 0, 2 * _np.pi,[-1,0,-1],[0,1,1])
    cutTubsLogical8 = _g4.LogicalVolume(cutTubsSolid8, 'G4_Cu', 'cutTubsLogical8')
    cutTubsPhysical8 = _g4.PhysicalVolume([0, 0, 0], [200, 0, 0], cutTubsLogical8, 'cutTubsPhysical8', worldLogical)

    cutTubsSolid9 = _g4.solid.CutTubs('cutTubs9', 0, 50, 50, 0, 2 * _np.pi,[-1,-1,-1],[1,1,1])
    cutTubsLogical9 = _g4.LogicalVolume(cutTubsSolid9, 'G4_Cu', 'cutTubsLogical9')
    cutTubsPhysical9 = _g4.PhysicalVolume([0, 0, 0], [200, 200, 0], cutTubsLogical9, 'cutTubsPhysical9', worldLogical)

    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')

    m = worldLogical.pycsgmesh()

    if vtkViewer:
        v = _vtk.Viewer()
        v.addPycsgMeshList(m)
        v.view();

    # write gdml
    if gdmlWriter:
        w = _gdml.Writer()
        w.addDetector(_g4.registry)
        w.write('./CutTubs.gdml')
        w.writeGmadTester('CutTubs.gmad')
