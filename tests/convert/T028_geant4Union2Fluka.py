import numpy as _np
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.geant4 as _g4
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi
import pathlib as _pl
import filecmp as _fc


def Test(
    vis=False, interactive=False, fluka=True, disjoint=False, outputPath=None, refFilePath=None
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "5", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "15", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    if not disjoint:
        us1 = _g4.solid.Union(
            "us1",
            bs,
            bs,
            [[0.0, _np.pi / 4, _np.pi / 4], [bx / 2, by / 2, bz / 2]],
            reg,
        )
        us2 = _g4.solid.Union(
            "us2",
            bs,
            us1,
            [[0.0, _np.pi / 4, _np.pi / 4], [bx / 2, by / 2, bz / 2]],
            reg,
        )
    else:
        us = _g4.solid.Union("us", bs, bs, [[0.0, 0.0, 0.0], [bx * 2, by * 2, bz * 2]], reg)
    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ul = _g4.LogicalVolume(us2, bm, "ul", reg)
    up = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ul, "u_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T028_geant4Union2Fluka.gdml")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    outputFile = outputPath / "T028_geant4Union2Fluka.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

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
