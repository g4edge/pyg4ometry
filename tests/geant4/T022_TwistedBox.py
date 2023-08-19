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

    tbx = _gd.Constant("bx", "10", reg, True)
    tby = _gd.Constant("by", "20", reg, True)
    tbz = _gd.Constant("bz", "30", reg, True)
    tbphit = _gd.Constant("bt", "1.0", reg, True)

    tbphit_deg = _gd.Constant("bt_deg", "1.0/pi*180", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    tm = _g4.MaterialPredefined("G4_Fe")

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        tm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        tm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.TwistedBox("ts", tbphit, tbx, tby, tbz, reg)

    assert ts.evaluateParameterWithUnits("twistedAngle") == tbphit
    assert ts.evaluateParameterWithUnits("pDx") == tbx
    assert ts.evaluateParameterWithUnits("pDy") == tby
    assert ts.evaluateParameterWithUnits("pDz") == tbz
    ts2 = _g4.solid.TwistedBox("ts2", tbphit_deg, tbx, tby, tbz, reg, "cm", "deg")
    assert ts2.evaluateParameterWithUnits("twistedAngle") == tbphit
    assert ts2.evaluateParameterWithUnits("pDx") == 10 * tbx
    assert ts2.evaluateParameterWithUnits("pDy") == 10 * tby
    assert ts2.evaluateParameterWithUnits("pDz") == 10 * tbz

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T022_TwistedBox.gdml"
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
