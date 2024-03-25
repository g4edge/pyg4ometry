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
    vis=True,
    interactive=False,
    fluka=True,
    outputPath=None,
    refFilePath=None,
    cuts=False,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)

    # pi        = _gd.Constant("pi","3.1415926",reg,True)
    trmin = _gd.Constant("trmin", "2.5", reg, True)
    trmax = _gd.Constant("trmax", "10.0", reg, True)
    tz = _gd.Constant("tz", "50", reg, True)
    tstartphi = _gd.Constant("startphi", "0", reg, True)
    tdeltaphi = _gd.Constant("deltaphi", "1.3*pi", reg, True)
    tlowx = _gd.Constant("ctlowx", "-1", reg, True)
    tlowy = _gd.Constant("ctlowy", "-1", reg, True)
    tlowz = _gd.Constant("ctlowz", "-1", reg, True)
    thighx = _gd.Constant("cthighx", "-1", reg, True)
    thighy = _gd.Constant("cthighy", "-1", reg, True)
    thighz = _gd.Constant("cthighz", "1", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    if cuts:
        ts = _g4.solid.CutTubs(
            "ts",
            trmin,
            trmax,
            tz,
            tstartphi,
            tdeltaphi,
            [tlowx, tlowy, tlowz],
            [thighx, thighy, thighz],
            reg,
            "mm",
            "rad",
        )
    else:
        ts = _g4.solid.CutTubs(
            "ts",
            0,
            trmax,
            tz,
            0,
            2 * _np.pi,
            [0, 0, -1],
            [0, 0, 1],
            reg,
            "mm",
            "rad",
        )

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)
    tp = _g4.PhysicalVolume([_np.pi / 4, 0.0, 0.0], [0, 25, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T003_geant4CutTubs2Fluka.gdml")

    # fluka conversion
    if not cuts and not bakeTransforms:
        outputFile = outputPath / "T003_geant4CutTubs2Fluka.inp"
    elif cuts and not bakeTransforms:
        outputFile = outputPath / "T003_geant4CutTubs2Fluka_cuts.inp"
    elif not cuts and bakeTransforms:
        outputFile = outputPath / "T003_geant4CutTubs2Fluka_baked.inp"
    elif cuts and bakeTransforms:
        outputFile = outputPath / "T003_geant4CutTubs2Fluka_cuts_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # flair output file
    f = _fluka.Flair("T003_geant4CutTubs2Fluka.inp", extentBB)
    f.write(outputPath / "T003_geant4CutTubs2Fluka.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
