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

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs1 = _g4.solid.Box("bs", 20 * bx, 20 * by, 20 * bz, reg, "mm")
    bs2 = _g4.solid.Box("bsp", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl1 = _g4.LogicalVolume(bs1, bm, "bl1", reg)
    bl2 = _g4.LogicalVolume(bs2, bm, "bl2", reg)
    bp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl1, "b_pv1", wl, reg)

    pbd1 = _g4.ParameterisedVolume.BoxDimensions(0.8 * bx, 0.8 * by, 0.4 * bz)
    pbp1 = _gd.Position("bp1", 0.0, 0.0, -8 * bx, "mm", reg)
    pbr1 = _gd.Rotation("br1", 0.0, 0.0, -0.4, "rad", reg)

    pbd2 = _g4.ParameterisedVolume.BoxDimensions(0.85 * bx, 0.85 * by, 0.5 * bz)
    pbp2 = _gd.Position("bp2", 0.0, 0.0, -6 * bx, "mm", reg)
    pbr2 = _gd.Rotation("br2", 0.0, 0.0, -0.3, "rad", reg)

    pbd3 = _g4.ParameterisedVolume.BoxDimensions(0.9 * bx, 0.9 * by, 0.6 * bz)
    pbp3 = _gd.Position("bp3", 0.0, 0.0, -4 * bx, "mm", reg)
    pbr3 = _gd.Rotation("br3", 0.0, 0.0, -0.2, "rad", reg)

    pbd4 = _g4.ParameterisedVolume.BoxDimensions(0.95 * bx, 0.95 * by, 0.7 * bz)
    pbp4 = _gd.Position("bp4", 0.0, 0.0, -2 * bx, "mm", reg)
    pbr4 = _gd.Rotation("br4", 0.0, 0.0, -0.1, "rad", reg)

    pbd5 = _g4.ParameterisedVolume.BoxDimensions(1.00 * bx, 1.00 * by, 0.8 * bz)
    pbp5 = _gd.Position("bp5", 0.0, 0.0, 0 * bx, "mm", reg)
    pbr5 = _gd.Rotation("br5", 0.0, 0.0, 0.0, "rad", reg)

    pbd6 = _g4.ParameterisedVolume.BoxDimensions(1.05 * bx, 1.05 * by, 0.9 * bz)
    pbp6 = _gd.Position("bp6", 0.0, 0.0, 2 * bx, "mm", reg)
    pbr6 = _gd.Rotation("br6", 0.0, 0.0, 0.1, "rad", reg)

    pbd7 = _g4.ParameterisedVolume.BoxDimensions(1.05 * bx, 1.05 * by, 1.0 * bz)
    pbp7 = _gd.Position("bp7", 0.0, 0.0, 4 * bx, "mm", reg)
    pbr7 = _gd.Rotation("br7", 0.0, 0.0, 0.2, "rad", reg)

    pbd8 = _g4.ParameterisedVolume.BoxDimensions(1.15 * bx, 1.15 * by, 1.1 * bz)
    pbp8 = _gd.Position("bp8", 0.0, 0.0, 6 * bx, "mm", reg)
    pbr8 = _gd.Rotation("br8", 0.0, 0.0, 0.3, "rad", reg)

    pbd9 = _g4.ParameterisedVolume.BoxDimensions(1.2 * bx, 1.2 * by, 1.2 * bz)
    pbp9 = _gd.Position("bp9", 0.0, 0.0, 8 * bx, "mm", reg)
    pbr9 = _gd.Rotation("br9", 0.0, 0.0, 0.4, "rad", reg)

    pbv = _g4.ParameterisedVolume(
        "pbv",
        bl2,
        bl1,
        9,
        [pbd1, pbd2, pbd3, pbd4, pbd5, pbd6, pbd7, pbd8, pbd9],
        [
            [pbr1, pbp1],
            [pbr2, pbp2],
            [pbr3, pbp3],
            [pbr4, pbp4],
            [pbr5, pbp5],
            [pbr6, pbp6],
            [pbr7, pbp7],
            [pbr8, pbp8],
            [pbr9, pbp9],
        ],
        reg,
    )

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T111_parameterised_box.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(pbv)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)
    extentParam = pbv.extent()

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
