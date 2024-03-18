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

    crmin1 = _gd.Constant("crmin1", "0", reg, True)
    crmax1 = _gd.Constant("crmax1", "20", reg, True)
    crmin2 = _gd.Constant("crmin2", "0", reg, True)
    crmax2 = _gd.Constant("crmax2", "10", reg, True)
    cz = _gd.Constant("cz", "50", reg, True)
    cdp = _gd.Constant("cdp", "2*pi", reg, True)
    zero = _gd.Constant("zero", "0.0", reg, False)

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
    cs = _g4.solid.Cons("cs", crmin1, crmax1, crmin2, crmax2, cz, zero, cdp, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    cl = _g4.LogicalVolume(cs, bm, "cl", reg)

    a = _random.random() * 2 * _np.pi
    b = _random.random() * 2 * _np.pi
    c = _random.random() * 2 * _np.pi

    for i in range(0, 5, 1):
        for j in range(0, 5, 1):
            for k in range(0, 5, 1):
                a = _random.random() * 2 * _np.pi
                b = _random.random() * 2 * _np.pi
                c = _random.random() * 2 * _np.pi

                bp = _g4.PhysicalVolume(
                    [a, b, c],
                    [5 * bx * (i - 2), 5 * by * (j - 2), 5 * bz * (k - 2)],
                    cl,
                    "b_pv_" + str(i) + "_" + str(j) + "_" + str(k),
                    wl,
                    reg,
                )

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T304_ManyCons.gdml"
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
    outputFile = outputPath / "T304_ManyCons.inp"
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
