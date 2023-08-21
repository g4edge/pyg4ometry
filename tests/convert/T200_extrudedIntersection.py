import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, fluka=True, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "10000", reg, True)
    wy = _gd.Constant("wy", "10000", reg, True)
    wz = _gd.Constant("wz", "10000", reg, True)

    polygon = [
        [0, 0],
        [0, 1000],
        [1000, 1000],
        [1000, 666],
        [333, 666],
        [333, 333],
        [1000, 333],
        [1000, 0],
    ]
    slices = [[-2000, [-500, -500], 1], [2000, [-500, -500], 1]]

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    xm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    xs = _g4.solid.ExtrudedSolid("xs", polygon, slices, reg, lunit="mm")
    cts = _g4.solid.CutTubs(
        "cts",
        0,
        2000,
        1000,
        0,
        2 * _np.pi,
        [0.25, 0, -1],
        [0.25, 0, 1],
        reg,
        lunit="mm",
    )
    ss = _g4.solid.Intersection("int", xs, cts, [[0, 0, 0], [0, 0, 0]], reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    xl = _g4.LogicalVolume(ss, xm, "xl", reg)
    xp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], xl, "x_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T200_extrudedIntersection.gdml")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # fluka conversion
    outputFile = outputPath / "T200_extrudedIntersection.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

        # flair output file
        f = _fluka.Flair(outputFile, extentBB)
        f.write(outputPath / "T200_extrudedIntersection.flair")

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

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
