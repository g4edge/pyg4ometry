import pyg4ometry as _pyg4
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vis
import pyg4ometry.gdml as _gdml
import vtk as _vtk
import numpy as _np


def test_Convert_mkVtkIdList(testdata, tmptestdir):
    id = [1, 2, 3, 4]

    vtkIdList = _pyg4.visualisation.mkVtkIdList(id)


def test_vtkPolyDataToNumpy(testdata, tmptestdir):
    reg = _g4.Registry()

    # defines
    wx = _gdml.Constant("wx", "100", reg, True)
    wy = _gdml.Constant("wy", "100", reg, True)
    wz = _gdml.Constant("wz", "100", reg, True)

    bx = _gdml.Constant("bx", "10", reg, True)
    by = _gdml.Constant("by", "10", reg, True)
    bz = _gdml.Constant("bz", "10", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    bs2 = _g4.solid.Box("bs2", bx, by, bz, reg, "cm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    v = _vis.VtkViewerNew()
    v.addLogicalVolume(reg.getWorldVolume())
    v.buildPipelinesAppend()

    pdNumpy = _vis.vtkPolyDataToNumpy(v.polydata["bl"])

    pdw = _vtk.vtkPolyDataWriter()
    pdw.SetInputData(v.polydata["bl"])
    pdw.SetFileName(str(tmptestdir / "temp.vtk"))

    pdNumpy = _vis.vtkPolyDataToNumpy(str(tmptestdir / "temp.vtk"))


def test_Convert_vtkTransformation2PyG4(testdata, tmptestdir):
    vt = _vtk.vtkTransform()

    [rot, tra] = _pyg4.visualisation.vtkTransformation2PyG4(vt)
