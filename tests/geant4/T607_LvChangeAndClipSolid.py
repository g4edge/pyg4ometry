import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _misc
import numpy as _np


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    wm = _g4.Material(name="G4_Galactic")
    bm = _g4.Material(name="G4_W")

    # solids
    ws = _g4.solid.Box("ws", 3, 3, 3, reg, "m")

    x = 1
    ds = _g4.solid.Box("ds", x, x, x, reg, "m")
    dds = _g4.solid.Box("dds", 0.2, 0.2, 0.2, reg, "m")

    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    dlv = _g4.LogicalVolume(ds, wm, "dlv", reg)
    ddlv = _g4.LogicalVolume(dds, bm, "ddlv", reg)

    nX = 4
    dX = x * 1000 / nX
    x0 = -0.5 * x * 1000 + 0.5 * dX
    for xi in [0, 1, 2, 3]:
        for yi in [0, 1, 2, 3]:
            pos = [x0 + xi * dX, x0 + yi * dX, 0]
            _g4.PhysicalVolume([0.1, 0.2, 0.3], pos, ddlv, "ddpv_" + str(xi) + str(yi), dlv, reg)

    _g4.PhysicalVolume([0, 0, 0.0], [0, 0, 0], dlv, "dlv_pv", wl, reg)

    # now for the culling
    # 800 should mean that the middle 4 out of 16 boxes remain untouched, but
    # the outer 12 should be intersected
    clipFW = 800
    rotation = [0, _np.pi / 4.0, _np.pi / 4.0]
    position = [0.4, 0.4, 0]
    clipBox = _g4.solid.Box("clipper", clipFW, clipFW, clipFW, reg, "mm")
    clipBoxes = _misc.NestedBoxes(
        "clipper", clipFW, clipFW, clipFW, reg, "mm", 50, 50, 50, dlv.depth()
    )

    dlv.replaceSolid(clipBoxes[0], rotation=rotation, position=position, punit="m")
    dlv.clipGeometry(clipBoxes, (0, 0, 0), (0, 0, 0))

    # set world volume
    reg.setWorld(wl)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T607_LvChangeAndClipSolid.gdml")

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addSolid(clipBoxes[0], rotation, position)
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test(vis=True)
