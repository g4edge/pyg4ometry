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

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    px = _gd.Constant("px", "10", reg, True)
    py = _gd.Constant("py", "20", reg, True)
    pz = _gd.Constant("pz", "30", reg, True)
    pAlpha = _gd.Constant("pAlpha", "0.2", reg, True)
    pTheta = _gd.Constant("pTheta", "0.3", reg, True)
    pPhi = _gd.Constant("pPhi", "0.4", reg, True)

    pAlpha_deg = _gd.Constant("pAlpha_deg", "0.2/pi*180", reg, True)
    pTheta_deg = _gd.Constant("pTheta_deg", "0.3/pi*180", reg, True)
    pPhi_deg = _gd.Constant("pPhi_deg", "0.4/pi*180", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    pm = _g4.MaterialPredefined("G4_Fe")
    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        pm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        pm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.Para("ps", px, py, pz, pAlpha, pTheta, pPhi, reg, "mm", "rad")
    assert ps.evaluateParameterWithUnits("pX") == px
    assert ps.evaluateParameterWithUnits("pY") == py
    assert ps.evaluateParameterWithUnits("pZ") == pz
    assert ps.evaluateParameterWithUnits("pAlpha") == pAlpha
    assert ps.evaluateParameterWithUnits("pPhi") == pPhi
    assert ps.evaluateParameterWithUnits("pTheta") == pTheta
    ps2 = _g4.solid.Para("ps2", px, py, pz, pAlpha_deg, pTheta_deg, pPhi_deg, reg, "cm", "deg")
    assert ps2.evaluateParameterWithUnits("pX") == 10 * px
    assert ps2.evaluateParameterWithUnits("pY") == 10 * py
    assert ps2.evaluateParameterWithUnits("pZ") == 10 * pz
    assert ps2.evaluateParameterWithUnits("pAlpha") == pAlpha
    assert ps2.evaluateParameterWithUnits("pPhi") == pPhi
    assert ps2.evaluateParameterWithUnits("pTheta") == pTheta

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    pp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T005_Para.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(ps)

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
