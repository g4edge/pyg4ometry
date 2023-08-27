import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    n_slice=30,
    writeNISTMaterials=False,
    outputPath=None,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    ex = _gd.Constant("ex", "10", reg, True)
    ey = _gd.Constant("ey", "25", reg, True)
    ez = _gd.Constant("ez", "20", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        em = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        em = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    es = _g4.solid.EllipticalTube("es", ex, ey, ez, reg, nslice=n_slice)
    assert es.evaluateParameterWithUnits("pDx") == ex
    assert es.evaluateParameterWithUnits("pDy") == ey
    assert es.evaluateParameterWithUnits("pDz") == ez
    es2 = _g4.solid.EllipticalTube("es2", ex, ey, ez, reg, "cm", nslice=n_slice)
    assert es2.evaluateParameterWithUnits("pDx") == 10 * ex
    assert es2.evaluateParameterWithUnits("pDy") == 10 * ey
    assert es2.evaluateParameterWithUnits("pDz") == 10 * ez

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    el = _g4.LogicalVolume(es, em, "el", reg)
    ep = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], el, "e_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T015_EllipticalTube.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(es)

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
