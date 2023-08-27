import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi

import T001_Box
import T031_MultiUnion


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg0 = _g4.Registry()

    l1 = T001_Box.Test(vis=False, interactive=False, outputPath=outputPath)["logicalVolume"]
    l2 = T031_MultiUnion.Test(vis=False, interactive=False, outputPath=outputPath)["logicalVolume"]

    wx0 = _gd.Constant("wx0", "200", reg0, True)
    wy0 = _gd.Constant("wy0", "200", reg0, True)
    wz0 = _gd.Constant("wz0", "200", reg0, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    ws = _g4.solid.Box("ws", wx0, wy0, wz0, reg0, "mm")
    wl = _g4.LogicalVolume(ws, wm, "wl", reg0)

    p1 = _g4.PhysicalVolume([0, 0, 0], [-50, 0, 0], l1, "l1_pv", wl, reg0)
    p2 = _g4.PhysicalVolume([0, 0, 0], [50, 0, 0], l2, "l2_pv", wl, reg0)

    reg0.addVolumeRecursive(p1)
    reg0.addVolumeRecursive(p2)

    reg0.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T431_MergeRegistry_MultiUnion.gdml"
    w = _gd.Writer()
    w.addDetector(reg0)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg0.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
