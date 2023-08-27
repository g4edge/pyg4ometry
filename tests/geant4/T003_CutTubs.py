import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
flat_ends = 2


def Test(
    vis=False,
    interactive=False,
    type=normal,
    n_slice=16,
    writeNISTMaterials=False,
    outputPath=None,
    outputFile=None,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    if not outputFile:
        outputFile = "T003_CutTubs.gdml"
    else:
        outputFile = _pl.Path(outputFile)

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi         = _gd.Constant("pi","3.1415926",reg,True)
    ctrmin = _gd.Constant("trmin", "2.5", reg, True)
    ctrmax = _gd.Constant("trmax", "10.0", reg, True)
    ctz = _gd.Constant("tz", "50", reg, True)
    ctstartphi = _gd.Constant("startphi", "0", reg, True)
    ctdeltaphi = _gd.Constant("deltaphi", "1.5*pi", reg, True)
    ctlowx = _gd.Constant("ctlowx", "-1", reg, True)
    ctlowy = _gd.Constant("ctlowy", "-1", reg, True)
    ctlowz = _gd.Constant("ctlowz", "-1", reg, True)
    cthighx = _gd.Constant("cthighx", "1", reg, True)
    cthighy = _gd.Constant("cthighy", "1", reg, True)
    cthighz = _gd.Constant("cthighz", "1", reg, True)

    ctstartphi_deg = _gd.Constant("startphi_deg", "0", reg, True)
    ctdeltaphi_deg = _gd.Constant("deltaphi_deg", "270", reg, True)

    expected_low = [-1, -1, -1]
    expected_high = [1, 1, 1]
    if type == flat_ends:
        ctlowx.setExpression(0)
        ctlowy.setExpression(0)
        ctlowz.setExpression(-1)
        cthighx.setExpression(0)
        cthighy.setExpression(0)
        cthighz.setExpression(1)
        expected_low = [0, 0, -1]
        expected_high = [0, 0, 1]

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        bm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    cts = _g4.solid.CutTubs(
        "ts",
        ctrmin,
        ctrmax,
        ctz,
        ctstartphi,
        ctdeltaphi,
        [ctlowx, ctlowy, ctlowz],
        [cthighx, cthighy, cthighz],
        reg,
        "mm",
        "rad",
        nslice=n_slice,
    )
    assert cts.evaluateParameterWithUnits("pRMin") == ctrmin
    assert cts.evaluateParameterWithUnits("pRMax") == ctrmax
    assert cts.evaluateParameterWithUnits("pDz") == ctz
    assert cts.evaluateParameterWithUnits("pSPhi") == ctstartphi
    assert cts.evaluateParameterWithUnits("pDPhi") == ctdeltaphi
    assert cts.evaluateParameterWithUnits("pLowNorm") == expected_low
    assert cts.evaluateParameterWithUnits("pHighNorm") == expected_high
    assert cts.evaluateParameterWithUnits("nslice") == n_slice
    cts2 = _g4.solid.CutTubs(
        "ts2",
        ctrmin,
        ctrmax,
        ctz,
        ctstartphi_deg,
        ctdeltaphi_deg,
        [ctlowx, ctlowy, ctlowz],
        [cthighx, cthighy, cthighz],
        reg,
        "cm",
        "deg",
        nslice=n_slice,
    )
    assert cts2.evaluateParameterWithUnits("pRMin") == 10 * ctrmin
    assert cts2.evaluateParameterWithUnits("pRMax") == 10 * ctrmax
    assert cts2.evaluateParameterWithUnits("pDz") == 10 * ctz
    assert cts2.evaluateParameterWithUnits("pSPhi") == ctstartphi
    assert cts2.evaluateParameterWithUnits("pDPhi") == ctdeltaphi
    assert cts2.evaluateParameterWithUnits("pLowNorm") == [10 * i for i in expected_low]
    assert cts2.evaluateParameterWithUnits("pHighNorm") == [10 * i for i in expected_high]
    assert cts2.evaluateParameterWithUnits("nslice") == n_slice

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ctl = _g4.LogicalVolume(cts, bm, "ctl", reg)
    ctp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ctl, "ct_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / outputFile
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(cts)

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
