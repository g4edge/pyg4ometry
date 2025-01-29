import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)

    b1pos = _gd.Position("b1pos", -bx, 0, 0, "mm", reg, True)
    b2pos = _gd.Position("b2pos", 0, 0, 0, "mm", reg, True)
    b2pos = _gd.Position("b3pos", bx, 0, 0, "mm", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs1 = _g4.solid.Box("bs1", 1.1 * bx, 0.9 * bx, 0.9 * bx, reg, "mm")
    bs2 = _g4.solid.Box("bs2", 1.1 * bx, 0.8 * bx, 0.8 * bx, reg, "mm")
    bs3 = _g4.solid.Box("bs3", 1.1 * bx, 0.7 * bx, 0.7 * bx, reg, "mm")

    rs = _g4.solid.Box("rs", 3 * bx, 2 * bx, 2 * bx, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl1 = _g4.LogicalVolume(bs1, bm, "bl1", reg)
    bl2 = _g4.LogicalVolume(bs2, bm, "bl2", reg)
    bl3 = _g4.LogicalVolume(bs3, bm, "bl3", reg)

    rl = _g4.LogicalVolume(rs, wm, "rl", reg)

    bp1 = _g4.PhysicalVolume([0.0, 0, 0], [-bx, 0, 0], bl1, "b_pv1", rl, reg)
    bp2 = _g4.PhysicalVolume([0.0, 0, 0], [0, 0, 0], bl2, "b_pv2", rl, reg)
    bp3 = _g4.PhysicalVolume([0.0, 0, 0], [bx, 0, 0], bl3, "b_pv3", rl, reg)

    rp1 = _g4.PhysicalVolume([0, 0, 0], [3 * bx, 0, 0], rl, "r_pv1", wl, reg)
    rp2 = _g4.PhysicalVolume([0, 0, 0], [-3 * bx, 0, 0], rl, "r_pv2", wl, reg, True, [-1, 1, 1])
    # check overlaps
    wl.checkOverlaps(recursive=True, coplanar=True)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T104_overlap_volu.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(bs1)

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
