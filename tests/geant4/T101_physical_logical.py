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

    r1pos = _gd.Position("r1pos", 0, -bx, 0, "mm", reg, True)
    r2pos = _gd.Position("r2pos", 0, 0, 0, "mm", reg, True)
    r3pos = _gd.Position("r3pos", 0, bx, 0, "mm", reg, True)

    l1pos = _gd.Position("l1pos", 0, 0, -bx, "mm", reg, True)
    l2pos = _gd.Position("l2pos", 0, 0, 0, "mm", reg, True)
    l3pos = _gd.Position("l3pos", 0, 0, bx, "mm", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, bx, bx, reg, "mm")
    rs = _g4.solid.Box("rs", 3 * bx, bx, bx, reg, "mm")
    ls = _g4.solid.Box("ls", 3 * bx, 3 * bx, bx, reg, "mm")
    cs = _g4.solid.Box("cs", 3 * bx, 3 * bx, 3 * bx, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    rl = _g4.LogicalVolume(rs, wm, "rl", reg)
    ll = _g4.LogicalVolume(ls, wm, "ll", reg)
    cl = _g4.LogicalVolume(cs, wm, "cl", reg)

    bp1 = _g4.PhysicalVolume([0, 0, 0], [-bx, 0, 0], bl, "b_pv1", rl, reg)
    bp2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv2", rl, reg)
    bp3 = _g4.PhysicalVolume([0, 0, 0], [bx, 0, 0], bl, "b_pv3", rl, reg)

    rp1 = _g4.PhysicalVolume([0, 0, 0], [0, -bx, 0], rl, "r_pv1", ll, reg)
    rp2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], rl, "r_pv2", ll, reg)
    rp3 = _g4.PhysicalVolume([0, 0, 0], [0, bx, 0], rl, "r_pv3", ll, reg)

    lp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, -bx], ll, "l_pv1", cl, reg)
    lp2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ll, "l_pv2", cl, reg)
    lp3 = _g4.PhysicalVolume([0, 0, 0], [0, 0, bx], ll, "l_pv3", cl, reg)

    cp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], cl, "c_pv1", wl, reg)

    # check for overlaps
    wl.checkOverlaps(True, True, False)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T101_physical_logical.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(bl)
    str(bp1)

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
