import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    v1 = _gd.Position("v1", "10", "10", "0", "mm", reg, True)
    v2 = _gd.Position("v2", "-10", "10", "0", "mm", reg, True)
    v3 = _gd.Position("v3", "-10", "-10", "0", "mm", reg, True)
    v4 = _gd.Position("v4", "0", "0", "10", "mm", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        tm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        tm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.Tet("ts", v1, v2, v3, v4, reg)
    assert ts.evaluateParameterWithUnits("anchor") == [10, 10, 0]
    assert ts.evaluateParameterWithUnits("p2") == [-10, 10, 0]
    assert ts.evaluateParameterWithUnits("p3") == [-10, -10, 0]
    assert ts.evaluateParameterWithUnits("p4") == [0, 0, 10]
    ts2 = _g4.solid.Tet("ts2", v1, v2, v3, v4, reg, "cm")
    assert ts2.evaluateParameterWithUnits("anchor") == [100, 100, 0]
    assert ts2.evaluateParameterWithUnits("p2") == [-100, 100, 0]
    assert ts2.evaluateParameterWithUnits("p3") == [-100, -100, 0]
    assert ts2.evaluateParameterWithUnits("p4") == [0, 0, 100]

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T020_Tet.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(ts)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"solid": ts, "testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
