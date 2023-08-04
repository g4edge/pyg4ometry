import os as _os
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import numpy as _np


def Test(vis=False, interactive=False):
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
            _g4.PhysicalVolume([0, 0, 0.0], pos, ddlv, "ddpv_" + str(xi) + str(yi), dlv, reg)

    _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], dlv, "dlv_pv", wl, reg)

    # now for the culling
    # 800 should mean that the middle 4 out of 16 boxes remain untouched, but
    # the outer 12 should be intersected
    clipFW = 800
    rotation = [_np.pi / 4, _np.pi / 4, _np.pi / 4]
    position = [250, 0, 0]
    clipBox = _g4.solid.Box("clipper", clipFW, clipFW, clipFW, reg, "mm")
    # dlv.changeSolidAndTrimGeometry(clipBox, rotation=rotation, position=position)
    [outside, inside, intersections] = dlv.clipGeometry(
        clipBox, rotation=rotation, position=position
    )

    # set world volume
    reg.setWorld(wl)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T604_lv_change_solid_and_trim_rot.gdml"))
    w.writeGmadTester(
        _os.path.join(_os.path.dirname(__file__)) + "T604_lv_change_solid_and_trim_rot.gmad",
        "T604_lv_change_solid_and_trim_rot.gdml",
    )

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addSolid(clipBox, rotation, position)

        """'
        i = 0
        print("outside")
        for m in outside :
            print(i,m)
            visOptions = _vi.VisualisationOptions()
            visOptions.colour = [1, 0, 0]
            visOptions.alpha = 0.0

            v.addMeshSimple(m,visOptions,name="outside_"+str(i))

            i=i+1

        i = 0
        print("intersection")
        for m in intersection :
            print(i,m)
            visOptions = _vi.VisualisationOptions()
            visOptions.colour = [0, 1, 0]
            visOptions.alpha = 0.0

            v.addMeshSimple(m,visOptions,name="inter_"+str(i))
            i=i+1

        i = 0
        print("inside")
        for m in inside :
            print(i,m)
            visOptions = _vi.VisualisationOptions()
            visOptions.colour = [0, 0, 1]
            visOptions.alpha = 0.0

            v.addMeshSimple(m,visOptions,name="inside_"+str(i))
            i=i+1
        """

        v.view(interactive=interactive)

    return reg, {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test(vis=True)
