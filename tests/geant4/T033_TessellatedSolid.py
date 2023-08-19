import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "5000", reg, True)
    wy = _gd.Constant("wy", "5000", reg, True)
    wz = _gd.Constant("wz", "5000", reg, True)

    p1 = [(-500, 500, 0), (500, 500, 0), (500, -500, 0), (-500, -500, 0)]
    p2 = [
        (-1000, 1000, 2000),
        (1000, 1000, 2000),
        (1000, -1000, 2000),
        (-1000, -1000, 2000),
    ]

    polygons = [p1, p2]

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        xm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        xm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    xtess = _g4.solid.createTessellatedSolid("test", polygons, reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tess_l = _g4.LogicalVolume(xtess, xm, "tess_l", reg)
    tess_p = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tess_l, "tess_p", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T033_TessellatedSolid.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(xtess)

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
