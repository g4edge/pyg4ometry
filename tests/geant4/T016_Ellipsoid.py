import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    n_slice=25,
    n_stack=25,
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
    eax = _gd.Constant("eax", "10", reg, True)
    eby = _gd.Constant("eby", "15", reg, True)
    ecz = _gd.Constant("ecz", "20", reg, True)
    ebc = _gd.Constant("ebc", "-15", reg, True)
    etc = _gd.Constant("etc", "15", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        em = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        em = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    es = _g4.solid.Ellipsoid("es", eax, eby, ecz, ebc, etc, reg, nslice=n_slice, nstack=n_stack)
    assert es.evaluateParameterWithUnits("pxSemiAxis") == eax
    assert es.evaluateParameterWithUnits("pySemiAxis") == eby
    assert es.evaluateParameterWithUnits("pzSemiAxis") == ecz
    assert es.evaluateParameterWithUnits("pzBottomCut") == ebc
    assert es.evaluateParameterWithUnits("pzTopCut") == etc
    es2 = _g4.solid.Ellipsoid(
        "es2", eax, eby, ecz, ebc, etc, reg, "cm", nslice=n_slice, nstack=n_stack
    )
    assert es2.evaluateParameterWithUnits("pxSemiAxis") == 10 * eax
    assert es2.evaluateParameterWithUnits("pySemiAxis") == 10 * eby
    assert es2.evaluateParameterWithUnits("pzSemiAxis") == 10 * ecz
    assert es2.evaluateParameterWithUnits("pzBottomCut") == 10 * ebc
    assert es2.evaluateParameterWithUnits("pzTopCut") == 10 * etc

    print(es.mesh())
    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    el = _g4.LogicalVolume(es, em, "el", reg)
    ep = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], el, "e_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T016_Ellipsoid.gdml"
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
