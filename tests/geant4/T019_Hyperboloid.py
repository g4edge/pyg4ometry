import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
rmin_eq_zero = 2
rmin_gt_rmax = 3


def Test(
    vis=False,
    interactive=False,
    type=normal,
    n_slice=16,
    n_stack=16,
    writeNISTMaterials=False,
    outputPath=None,
    outputFile=None,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    if not outputFile:
        outputFile = "T019_Hyperboloid.gdml"
    else:
        outputFile = _pl.Path(outputFile)

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    pi = _gd.Constant("pi", "3.1415926", reg, True)
    hrmin = _gd.Constant("hrmin", "20", reg, True)
    hrmax = _gd.Constant("hrmax", "30.0", reg, True)
    hz = _gd.Constant("hz", "50.0", reg, True)
    hinst = _gd.Constant("hinst", "0.7", reg, True)
    houtst = _gd.Constant("houtst", "0.7", reg, True)

    hinst_deg = _gd.Constant("hinst_deg", "0.7/pi*180", reg, True)
    houtst_deg = _gd.Constant("houtst_deg", "0.7/pi*180", reg, True)

    if type == rmin_eq_zero:
        hrmin.setExpression(0)

    if type == rmin_gt_rmax:
        hrmin.setExpression(2)
        hrmax.setExpression(1)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        hm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        hm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    hs = _g4.solid.Hype("hs", hrmin, hrmax, hinst, houtst, hz, reg, nslice=n_slice, nstack=n_stack)
    assert hs.evaluateParameterWithUnits("innerRadius") == hrmin
    assert hs.evaluateParameterWithUnits("outerRadius") == hrmax
    assert hs.evaluateParameterWithUnits("innerStereo") == hinst
    assert hs.evaluateParameterWithUnits("outerStereo") == houtst
    assert hs.evaluateParameterWithUnits("lenZ") == hz
    hs2 = _g4.solid.Hype(
        "hs2",
        hrmin,
        hrmax,
        hinst,
        houtst,
        hz,
        reg,
        "cm",
        nslice=n_slice,
        nstack=n_stack,
    )
    assert hs2.evaluateParameterWithUnits("innerRadius") == 10 * hrmin
    assert hs2.evaluateParameterWithUnits("outerRadius") == 10 * hrmax
    assert hs2.evaluateParameterWithUnits("innerStereo") == hinst
    assert hs2.evaluateParameterWithUnits("outerStereo") == houtst
    assert hs2.evaluateParameterWithUnits("lenZ") == 10 * hz

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    hl = _g4.LogicalVolume(hs, hm, "hl", reg)
    hp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], hl, "h_pv1", wl, reg)

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
    str(hs)

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
