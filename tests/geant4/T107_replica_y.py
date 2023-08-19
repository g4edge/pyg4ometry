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
    wx = _gd.Constant("wx", "1000", reg, True)
    wy = _gd.Constant("wy", "1000", reg, True)
    wz = _gd.Constant("wz", "1000", reg, True)

    bx = _gd.Constant("bx", "100", reg, True)
    by = _gd.Constant("by", "100", reg, True)
    bz = _gd.Constant("bz", "100", reg, True)

    mbx = _gd.Constant("mbx", "100", reg, True)
    mby = _gd.Constant("mby", "800", reg, True)
    mbz = _gd.Constant("mbz", "100", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    mbs = _g4.solid.Box("mbs", mbx, mby, mbz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    ml = _g4.LogicalVolume(mbs, wm, "ml", reg)
    mbl = _g4.ReplicaVolume(
        "mbl", bl, ml, _g4.ReplicaVolume.Axis.kYAxis, 8, 100, 0, reg, True, "mm", "mm"
    )

    mbp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ml, "ml_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T107_replica_y.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

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
