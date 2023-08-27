import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi

normal = 1
zero_area_quad = 2


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi    = _gd.Constant("pi","3.1415926",reg,True)

    tv1x = _gd.Constant("v1x", "10", reg, True)
    tv1y = _gd.Constant("v1y", "10", reg, True)

    tv2x = _gd.Constant("v2x", "20", reg, True)
    tv2y = _gd.Constant("v2y", "30", reg, True)

    tv3x = _gd.Constant("v3x", "30", reg, True)
    tv3y = _gd.Constant("v3y", "30", reg, True)

    tv4x = _gd.Constant("v4x", "40", reg, True)
    tv4y = _gd.Constant("v4y", "10", reg, True)

    tv5x = _gd.Constant("v5x", "20", reg, True)
    tv5y = _gd.Constant("v5y", "20", reg, True)

    tv6x = _gd.Constant("v6x", "20", reg, True)
    tv6y = _gd.Constant("v6y", "40", reg, True)

    tv7x = _gd.Constant("v7x", "40", reg, True)
    tv7y = _gd.Constant("v7y", "40", reg, True)

    tv8x = _gd.Constant("v8x", "40", reg, True)
    tv8y = _gd.Constant("v8y", "20", reg, True)

    tz = _gd.Constant("z", "30", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        tm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.Material(name="G4_Galactic")
        tm = _g4.Material(name="G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.GenericTrap(
        "ts",
        tv1x,
        tv1y,
        tv2x,
        tv2y,
        tv3x,
        tv3y,
        tv4x,
        tv4y,
        tv5x,
        tv5y,
        tv6x,
        tv6y,
        tv7x,
        tv7y,
        tv8x,
        tv8y,
        tz,
        reg,
        lunit="mm",
    )
    assert ts.evaluateParameterWithUnits("v1x") == tv1x
    assert ts.evaluateParameterWithUnits("v1y") == tv1y
    assert ts.evaluateParameterWithUnits("v2x") == tv2x
    assert ts.evaluateParameterWithUnits("v2y") == tv2y
    assert ts.evaluateParameterWithUnits("v3x") == tv3x
    assert ts.evaluateParameterWithUnits("v3y") == tv3y
    assert ts.evaluateParameterWithUnits("v4x") == tv4x
    assert ts.evaluateParameterWithUnits("v4y") == tv4y
    assert ts.evaluateParameterWithUnits("v5x") == tv5x
    assert ts.evaluateParameterWithUnits("v5y") == tv5y
    assert ts.evaluateParameterWithUnits("v6x") == tv6x
    assert ts.evaluateParameterWithUnits("v6y") == tv6y
    assert ts.evaluateParameterWithUnits("v7x") == tv7x
    assert ts.evaluateParameterWithUnits("v7y") == tv7y
    assert ts.evaluateParameterWithUnits("v8x") == tv8x
    assert ts.evaluateParameterWithUnits("v8y") == tv8y
    assert ts.evaluateParameterWithUnits("dz") == tz
    ts2 = _g4.solid.GenericTrap(
        "ts2",
        tv1x,
        tv1y,
        tv2x,
        tv2y,
        tv3x,
        tv3y,
        tv4x,
        tv4y,
        tv5x,
        tv5y,
        tv6x,
        tv6y,
        tv7x,
        tv7y,
        tv8x,
        tv8y,
        tz,
        reg,
        lunit="cm",
    )
    assert ts2.evaluateParameterWithUnits("v1x") == 10 * tv1x
    assert ts2.evaluateParameterWithUnits("v1y") == 10 * tv1y
    assert ts2.evaluateParameterWithUnits("v2x") == 10 * tv2x
    assert ts2.evaluateParameterWithUnits("v2y") == 10 * tv2y
    assert ts2.evaluateParameterWithUnits("v3x") == 10 * tv3x
    assert ts2.evaluateParameterWithUnits("v3y") == 10 * tv3y
    assert ts2.evaluateParameterWithUnits("v4x") == 10 * tv4x
    assert ts2.evaluateParameterWithUnits("v4y") == 10 * tv4y
    assert ts2.evaluateParameterWithUnits("v5x") == 10 * tv5x
    assert ts2.evaluateParameterWithUnits("v5y") == 10 * tv5y
    assert ts2.evaluateParameterWithUnits("v6x") == 10 * tv6x
    assert ts2.evaluateParameterWithUnits("v6y") == 10 * tv6y
    assert ts2.evaluateParameterWithUnits("v7x") == 10 * tv7x
    assert ts2.evaluateParameterWithUnits("v7y") == 10 * tv7y
    assert ts2.evaluateParameterWithUnits("v8x") == 10 * tv8x
    assert ts2.evaluateParameterWithUnits("v8y") == 10 * tv8y
    assert ts2.evaluateParameterWithUnits("dz") == 10 * tz

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T026_GenericTrap.gdml"
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

    return {"teststatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
