import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi


def Test(
    vis=False,
    interactive=False,
    n_slice=20,
    n_stack=20,
    scale=[-1, 1, 1],
    title="T114_physical_reflection_x",
    outputPath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)
    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    trmin = _gd.Constant("rmin", "2.0", reg, True)
    trmax = _gd.Constant("rmax", "10.0", reg, True)
    trtor = _gd.Constant("rtor", "40.0", reg, True)
    tsphi = _gd.Constant("sphi", "0.05*pi/2.0", reg, True)
    tdphi = _gd.Constant("dphi", "0.9*pi/2.0", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    tm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.Torus(
        "ts",
        trmin,
        trmax,
        trtor,
        tsphi,
        tdphi,
        reg,
        "mm",
        "rad",
        nslice=n_slice,
        nstack=n_stack,
    )

    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    us = _g4.solid.Union("us", bs, bs, [[0.1, 0.2, 0.3], [bx / 2, by / 2, bz / 2]], reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    ul = _g4.LogicalVolume(us, tm, "ul", reg)
    tp1 = _g4.PhysicalVolume([0, 0, 0], [20, 20, 20], tl, "t_pv1", wl, reg)
    tp2 = _g4.PhysicalVolume([0, 0, 0], [20, 20, 20], tl, "t_pv2", wl, reg, scale=scale)
    up = _g4.PhysicalVolume([0, 0, 0], [20, 10, 60], ul, "u_pv1", wl, reg)
    up2 = _g4.PhysicalVolume([0, 0, 0], [20, 10, 60], ul, "u_pv2", wl, reg, scale=scale)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / title / ".gdml")

    # test __repr__
    str(ts)

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
