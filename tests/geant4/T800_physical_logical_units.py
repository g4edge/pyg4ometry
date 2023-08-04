import os as _os
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi


def Test(vis=False, interactive=False):
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)
    bx = _gd.Constant("bx", "10", reg, True)

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

    bp1 = _g4.PhysicalVolume([0, 0, 0, "rad"], [-bx, 0, 0, "mm"], bl, "b_pv1", rl, reg)
    bp2 = _g4.PhysicalVolume([0, 0, 0, "mrad"], [0, 0, 0, "m"], bl, "b_pv2", rl, reg)
    bp3 = _g4.PhysicalVolume([0, 0, 0, "urad"], [bx, 0, 0, "mm"], bl, "b_pv3", rl, reg)

    rp1 = _g4.PhysicalVolume([0, 0, 0, "rad"], [0, -bx / 3, 0, "cm"], rl, "r_pv1", ll, reg)
    rp2 = _g4.PhysicalVolume([0, 0, 0, "mrad"], [0, 0, 0, "um"], rl, "r_pv2", ll, reg)
    rp3 = _g4.PhysicalVolume([100, 0, 0, "urad"], [0, bx, 0, "mm"], rl, "r_pv3", ll, reg)

    lp1 = _g4.PhysicalVolume([0, 0, 0, "rad"], [0, 0, -bx, "mm"], ll, "l_pv1", cl, reg)
    lp2 = _g4.PhysicalVolume([0, 0, 0, "mrad"], [0, 0, 0, "um"], ll, "l_pv2", cl, reg)
    lp3 = _g4.PhysicalVolume([0, 0, 0, "urad"], [0, 0, bx, "mm"], ll, "l_pv3", cl, reg)

    cp1 = _g4.PhysicalVolume([0, 0, 0, "rad"], [0, 0, 0, "mm"], cl, "c_pv1", wl, reg)

    # check for overlaps
    wl.checkOverlaps(True, True, False)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T800_physical_logical_units.gdml"))

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
    Test(1, 1)
