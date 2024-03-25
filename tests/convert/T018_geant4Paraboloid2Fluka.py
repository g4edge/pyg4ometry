import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np
import filecmp as _fc


def Test(
    vis=False,
    interactive=False,
    fluka=True,
    n_slice=16,
    n_stack=16,
    outputPath=None,
    refFilePath=None,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)

    # pi   = _gd.Constant("pi","3.1415926",reg,True)
    prlo = _gd.Constant("prlo", "2", reg, True)
    prhi = _gd.Constant("prhi", "15", reg, True)
    pz = _gd.Constant("pz", "50", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    pm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.Paraboloid("ps", pz, prlo, prhi, reg, nslice=n_slice, nstack=n_stack)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    pp = _g4.PhysicalVolume([_np.pi / 4, 0, 0], [0, 25, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T018_geant4Paraboloid2Fluka.gdml")

    # fluka conversion
    if not bakeTransforms:
        outputFile = outputPath / "T018_geant4Paraboloid2Fluka.inp"
    else:
        outputFile = outputPath / "T018_geant4Paraboloid2Fluka_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # flair output file
    f = _fluka.Flair("T018_geant4Paraboloid2Fluka.inp", extentBB)
    f.write(outputPath / "T018_geant4Paraboloid2Fluka.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    if refFilePath is not None:
        assert _fc.cmp(refFilePath, outputPath / outputFile, shallow=False)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
