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

    bx = _gd.Constant("bx", "25", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", 1.0 * bx, 1.0 * bx, 1.0 * bx, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl = _g4.LogicalVolume(bs, bm, "bl", reg)

    bp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)
    bp2 = _g4.PhysicalVolume([0, 0.3, 0], [0, bx, 0], bl, "b_pv2", wl, reg)

    # check for overlaps
    wl.checkOverlaps(recursive=True, coplanar=True, debugIO=False)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T103_overlap_copl_simple.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(bs)

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
