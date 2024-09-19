import os as _os
import pathlib as _pl
import numpy as _np
from ast import literal_eval as _literal_eval

import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka

import random as _random


def Test(
    vis=False,
    interactive=False,
    writeNISTMaterials=False,
    outputPath=None,
    fluka=True,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "1000", reg, True)
    wy = _gd.Constant("wy", "1000", reg, True)
    wz = _gd.Constant("wz", "1000", reg, True)

    bx = _gd.Constant("bx", "40", reg, True)
    by = _gd.Constant("by", "40", reg, True)
    bz = _gd.Constant("bz", "40", reg, True)

    trmin = _gd.Constant("trmin", "0", reg, True)
    trmax = _gd.Constant("trmax", "51.0", reg, True)
    tz = _gd.Constant("tz", "51", reg, True)
    tstartphi = _gd.Constant("startphi", "0", reg, True)
    tdeltaphi = _gd.Constant("deltaphi", "2*pi", reg, True)
    ts = _g4.solid.Tubs("ts", trmin, trmax, tz, tstartphi, tdeltaphi, reg, "mm", "rad")

    trmin2 = _gd.Constant("trmin2", "25", reg, True)
    trmax2 = _gd.Constant("trmax2", "50.0", reg, True)
    tz2 = _gd.Constant("tz2", "50", reg, True)
    tstartphi2 = _gd.Constant("startphi2", "0", reg, True)
    tdeltaphi2 = _gd.Constant("deltaphi2", "3*pi/2", reg, True)
    ts2 = _g4.solid.Tubs("ts2", trmin2, trmax2, tz2, tstartphi2, tdeltaphi2, reg, "mm", "rad")

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        bm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "bl", reg)
    tl2 = _g4.LogicalVolume(ts2, bm, "bl2", reg)

    bp2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl2, "b2_pv", tl, reg)

    a = _random.random() * 2 * _np.pi
    b = _random.random() * 2 * _np.pi
    c = _random.random() * 2 * _np.pi

    iP = 0
    iMax = 125
    for i in range(0, 5, 1):
        for j in range(0, 5, 1):
            for k in range(0, 5, 1):
                a = _random.random() * 2 * _np.pi
                b = _random.random() * 2 * _np.pi
                c = _random.random() * 2 * _np.pi

                if iP < iMax:
                    bp = _g4.PhysicalVolume(
                        [a, b, c],
                        [5 * bx * (i - 2), 5 * by * (j - 2), 5 * bz * (k - 2)],
                        tl,
                        "b_pv_" + str(i) + "_" + str(j) + "_" + str(k),
                        wl,
                        reg,
                    )
                iP = iP + 1

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T301_ManyTubs.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.PubViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    # fluka conversion
    outputFile = outputPath / "T301_ManyTubs.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)

        # fluka running
        freg.addDefaults(default="PRECISIO")
        freg.addBeam(energy=10)
        freg.addBeamPos()
        freg.addUsrBin(name="bin1")
        freg.addUsrBin(name="bin2")
        freg.addLowMatAllMaterials()
        # freg.addLowPwxs()
        freg.addRandomiz()
        freg.addStart(maxPrimHistories=100)

        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)


if __name__ == "__main__":
    Test()
