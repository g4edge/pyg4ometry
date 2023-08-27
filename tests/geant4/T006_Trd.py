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

    tx1 = _gd.Constant("tx1", "20", reg, True)
    ty1 = _gd.Constant("ty1", "25", reg, True)
    tx2 = _gd.Constant("tx2", "5", reg, True)
    ty2 = _gd.Constant("ty2", "7.5", reg, True)
    tz = _gd.Constant("tz", "10.0", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        tm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        tm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.Trd("ts", tx1, tx2, ty1, ty2, tz, reg, "mm")
    assert ts.evaluateParameterWithUnits("pX1") == tx1
    assert ts.evaluateParameterWithUnits("pX2") == tx2
    assert ts.evaluateParameterWithUnits("pY1") == ty1
    assert ts.evaluateParameterWithUnits("pY2") == ty2
    assert ts.evaluateParameterWithUnits("pZ") == tz
    ts2 = _g4.solid.Trd("ts2", tx1, tx2, ty1, ty2, tz, reg, "cm")
    assert ts2.evaluateParameterWithUnits("pX1") == 10 * tx1
    assert ts2.evaluateParameterWithUnits("pX2") == 10 * tx2
    assert ts2.evaluateParameterWithUnits("pY1") == 10 * ty1
    assert ts2.evaluateParameterWithUnits("pY2") == 10 * ty2
    assert ts2.evaluateParameterWithUnits("pZ") == 10 * tz

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T006_Trd.gdml"
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

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
