import os as _os
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi


def Test(vis=False, interactive=False):
    reg = _g4.Registry()

    mbx = _gd.Constant("mbx", "800", reg, True)
    mby = _gd.Constant("mby", "100", reg, True)
    mbz = _gd.Constant("mbz", "100", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", 1000, 1000, 1000, reg)
    bs = _g4.solid.Box("bs", 100, 100, 100, reg)
    mbs = _g4.solid.Box("mbs", mbx, mby, mbz, reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    ml = _g4.LogicalVolume(mbs, wm, "ml", reg)
    ml2 = _g4.LogicalVolume(mbs, wm, "ml2", reg)
    mbl = _g4.ReplicaVolume(
        "mbl", bl, ml, _g4.ReplicaVolume.Axis.kXAxis, 8, 100, 0, reg, True, "mm", "mm"
    )

    # the replica mother overlaps with another big box with no contents
    mbp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ml, "ml_pv1", wl, reg)
    mbp = _g4.PhysicalVolume([0, 0, 0], [0, 40, 0], ml2, "ml2_pv1", wl, reg)

    wl.checkOverlaps(recursive=True, coplanar=True)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T106_replica_x.gdml"))

    # test __repr__
    str(mbl)

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
