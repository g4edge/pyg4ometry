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

    ttwist = _gd.Constant("tptwist", "1.0", reg, True)

    tx1 = _gd.Constant("tx1", "5", reg, True)
    tx2 = _gd.Constant("tx2", "5", reg, True)
    tx3 = _gd.Constant("tx3", "10", reg, True)
    tx4 = _gd.Constant("tx4", "10", reg, True)

    ty1 = _gd.Constant("ty1", "5", reg, True)
    ty2 = _gd.Constant("ty2", "7.5", reg, True)

    tz = _gd.Constant("tz", "10.0", reg, True)

    ttheta = _gd.Constant("ttheta", "0.6", reg, True)
    tphi = _gd.Constant("tphi", "0.0", reg, True)
    talp = _gd.Constant("talp", "0.0", reg, True)

    ttwist_deg = _gd.Constant("tptwist_deg", "1.0/pi*180", reg, True)
    ttheta_deg = _gd.Constant("ttheta_deg", "0.6/pi*180", reg, True)
    tphi_deg = _gd.Constant("tphi_deg", "0.0/pi*180", reg, True)
    talp_deg = _gd.Constant("talp_deg", "0.0/pi*180", reg, True)

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
    ts = _g4.solid.TwistedTrap(
        "ts", ttwist, tz, ttheta, tphi, ty1, tx1, tx2, ty2, tx3, tx4, talp, reg
    )

    assert ts.evaluateParameterWithUnits("twistedAngle") == ttwist
    assert ts.evaluateParameterWithUnits("pDz") == tz
    assert ts.evaluateParameterWithUnits("pTheta") == ttheta
    assert ts.evaluateParameterWithUnits("pDPhi") == tphi
    assert ts.evaluateParameterWithUnits("pDy1") == ty1
    assert ts.evaluateParameterWithUnits("pDx1") == tx1
    assert ts.evaluateParameterWithUnits("pDx2") == tx2
    assert ts.evaluateParameterWithUnits("pDy2") == ty2
    assert ts.evaluateParameterWithUnits("pDx3") == tx3
    assert ts.evaluateParameterWithUnits("pDx4") == tx4
    assert ts.evaluateParameterWithUnits("pAlp") == talp
    ts2 = _g4.solid.TwistedTrap(
        "ts2",
        ttwist_deg,
        tz,
        ttheta_deg,
        tphi_deg,
        ty1,
        tx1,
        tx2,
        ty2,
        tx3,
        tx4,
        talp_deg,
        reg,
        "cm",
        "deg",
    )
    assert ts2.evaluateParameterWithUnits("twistedAngle") == ttwist
    assert ts2.evaluateParameterWithUnits("pDz") == 10 * tz
    assert ts2.evaluateParameterWithUnits("pTheta") == ttheta
    assert ts2.evaluateParameterWithUnits("pDPhi") == tphi
    assert ts2.evaluateParameterWithUnits("pDy1") == 10 * ty1
    assert ts2.evaluateParameterWithUnits("pDx1") == 10 * tx1
    assert ts2.evaluateParameterWithUnits("pDx2") == 10 * tx2
    assert ts2.evaluateParameterWithUnits("pDy2") == 10 * ty2
    assert ts2.evaluateParameterWithUnits("pDx3") == 10 * tx3
    assert ts2.evaluateParameterWithUnits("pDx4") == 10 * tx4
    assert ts2.evaluateParameterWithUnits("pAlp") == talp

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T023_TwistedTrap.gdml"
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
