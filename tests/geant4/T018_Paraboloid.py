import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    n_slice=16,
    n_stack=16,
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

    # pi   = _gd.Constant("pi","3.1415926",reg,True)
    prlo = _gd.Constant("prlo", "2", reg, True)
    prhi = _gd.Constant("prhi", "15", reg, True)
    pz = _gd.Constant("pz", "50", reg, True)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        pm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        pm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.Paraboloid("ps", pz, prlo, prhi, reg, nslice=n_slice, nstack=n_stack)
    assert ps.evaluateParameterWithUnits("pDz") == pz
    assert ps.evaluateParameterWithUnits("pR1") == prlo
    assert ps.evaluateParameterWithUnits("pR2") == prhi
    ps2 = _g4.solid.Paraboloid("ps2", pz, prlo, prhi, reg, "cm", nslice=n_slice, nstack=n_stack)
    assert ps2.evaluateParameterWithUnits("pDz") == 10 * pz
    assert ps2.evaluateParameterWithUnits("pR1") == 10 * prlo
    assert ps2.evaluateParameterWithUnits("pR2") == 10 * prhi

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    pp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T018_Paraboloid.gdml"
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

    return {"teststatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
