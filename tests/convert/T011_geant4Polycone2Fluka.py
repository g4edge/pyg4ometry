import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    fluka=True,
    n_slice=10,
    outputPath=None,
    refFilePath=None,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    psphi = _gd.Constant("sphi", "0", reg, True)
    pdphi = _gd.Constant("dphi", "1.5*pi", reg, True)

    prmin1 = _gd.Constant("prmin1", "7", reg, True)
    prmax1 = _gd.Constant("prmax1", "9", reg, True)
    pz1 = _gd.Constant("z1", "-10", reg, True)

    prmin2 = _gd.Constant("prmin2", "5", reg, True)
    prmax2 = _gd.Constant("prmax2", "9", reg, True)
    pz2 = _gd.Constant("z2", "0", reg, True)

    prmin3 = _gd.Constant("prmin3", "4", reg, True)
    prmax3 = _gd.Constant("prmax3", "5", reg, True)
    pz3 = _gd.Constant("z3", "10", reg, True)

    prmin = [prmin1, prmin2, prmin3]
    prmax = [prmax1, prmax2, prmax3]
    pz = [pz1, pz2, pz3]

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    pm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.Polycone("ps", psphi, pdphi, pz, prmin, prmax, reg, "mm", "rad", nslice=n_slice)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    tp = _g4.PhysicalVolume([_np.pi / 4, 0, 0], [0, 10, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T011_geant4Polycone2Fluka.gdml")

    # fluka conversion
    if not bakeTransforms:
        outputFile = outputPath / "T011_geant4Polycone2Fluka.inp"
    else:
        outputFile = outputPath / "T011_geant4Polycone2Fluka_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # flair output file
    f = _fluka.Flair(outputFile, extentBB)
    f.write(str(outputPath / "T011_geant4Polycone2Fluka.flair"))

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
