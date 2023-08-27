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

    # pi        = _gd.Constant("pi","3.1415926",reg,True)

    ttwist = _gd.Constant("tptwist", "1.0", reg, True)
    trmin = _gd.Constant("trmin", "2.5", reg, True)
    trmax = _gd.Constant("trmax", "10.0", reg, True)
    tz = _gd.Constant("tz", "50", reg, True)
    tphi = _gd.Constant("phi", "1.5*pi", reg, True)

    ttwist_deg = _gd.Constant("tptwist_deg", "1.0/pi*180", reg, True)
    tphi_deg = _gd.Constant("tphi_deg", "1.5*180", reg, True)

    wm = _g4.Material(name="G4_Galactic")
    bm = _g4.Material(name="G4_Fe")

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        bm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.Material(name="G4_Galactic")
        bm = _g4.Material(name="G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.TwistedTubs("ts", trmin, trmax, tz, tphi, ttwist, reg)
    assert ts.evaluateParameterWithUnits("endinnerrad") == trmin
    assert ts.evaluateParameterWithUnits("endouterrad") == trmax
    assert ts.evaluateParameterWithUnits("zlen") == tz
    assert ts.evaluateParameterWithUnits("phi") == tphi
    assert ts.evaluateParameterWithUnits("twistedangle") == ttwist
    ts2 = _g4.solid.TwistedTubs("ts2", trmin, trmax, tz, tphi_deg, ttwist_deg, reg, "cm", "deg")
    assert ts2.evaluateParameterWithUnits("endinnerrad") == 10 * trmin
    assert ts2.evaluateParameterWithUnits("endouterrad") == 10 * trmax
    assert ts2.evaluateParameterWithUnits("zlen") == 10 * tz
    assert ts2.evaluateParameterWithUnits("phi") == tphi
    assert ts2.evaluateParameterWithUnits("twistedangle") == ttwist

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T025_TwistedTubs.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

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

    return {"teststatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
