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

    pRMin = _gd.Constant("pRMin", "5", reg, True)
    pRMax = _gd.Constant("pRMax", "25", reg, True)
    pDz = _gd.Constant("pDz", "50", reg, True)
    pSPhi = _gd.Constant("pSPhi", "0", reg, True)
    pDPhi = _gd.Constant("pDPhi", "2*pi", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs1 = _g4.solid.Box("bs", 20 * bx, 20 * by, 20 * bz, reg, "mm")
    ts2 = _g4.solid.Tubs("tsp", pRMin, pRMax, pDz, pSPhi, pDPhi, reg, "mm", "rad")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl1 = _g4.LogicalVolume(bs1, bm, "bl1", reg)
    tl2 = _g4.LogicalVolume(ts2, bm, "tl2", reg)
    bp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl1, "b_pv1", wl, reg)

    ptd1 = _g4.ParameterisedVolume.TubeDimensions(0.1, 1.0, 2.5, 0, "2*pi*0.1", "mm", "rad")
    ptp1 = _gd.Position("bp1", 0.0, 0.0, -8 * bx, "mm", reg)
    ptr1 = _gd.Rotation("br1", 0.0, 0.0, -0.4, "rad", reg)

    ptd2 = _g4.ParameterisedVolume.TubeDimensions(0.2, 1.2, 2.5, 0, "2*pi*0.2", "mm", "rad")
    ptp2 = _gd.Position("bp2", 0.0, 0.0, -6 * bx, "mm", reg)
    ptr2 = _gd.Rotation("br2", 0.0, 0.0, -0.3, "rad", reg)

    ptd3 = _g4.ParameterisedVolume.TubeDimensions(0.3, 1.4, 2.5, 0, "2*pi*0.3", "mm", "rad")
    ptp3 = _gd.Position("bp3", 0.0, 0.0, -4 * bx, "mm", reg)
    ptr3 = _gd.Rotation("br3", 0.0, 0.0, -0.2, "rad", reg)

    ptd4 = _g4.ParameterisedVolume.TubeDimensions(0.4, 1.6, 2.5, 0, "2*pi*0.4", "mm", "rad")
    ptp4 = _gd.Position("bp4", 0.0, 0.0, -2 * bx, "mm", reg)
    ptr4 = _gd.Rotation("br4", 0.0, 0.0, -0.1, "rad", reg)

    ptd5 = _g4.ParameterisedVolume.TubeDimensions(0.5, 1.8, 2.5, 0, "2*pi*0.5", "mm", "rad")
    ptp5 = _gd.Position("bp5", 0.0, 0.0, 0 * bx, "mm", reg)
    ptr5 = _gd.Rotation("br5", 0.0, 0.0, 0.0, "rad", reg)

    ptd6 = _g4.ParameterisedVolume.TubeDimensions(0.6, 2.0, 2.5, 0, "2*pi*0.6", "mm", "rad")
    ptp6 = _gd.Position("bp6", 0.0, 0.0, 2 * bx, "mm", reg)
    ptr6 = _gd.Rotation("br6", 0.0, 0.0, 0.1, "rad", reg)

    ptd7 = _g4.ParameterisedVolume.TubeDimensions(0.7, 2.2, 2.5, 0, "2*pi*0.7", "mm", "rad")
    ptp7 = _gd.Position("bp7", 0.0, 0.0, 4 * bx, "mm", reg)
    ptr7 = _gd.Rotation("br7", 0.0, 0.0, 0.2, "rad", reg)

    ptd8 = _g4.ParameterisedVolume.TubeDimensions(0.8, 2.4, 2.5, 0, "2*pi*0.8", "mm", "rad")
    ptp8 = _gd.Position("bp8", 0.0, 0.0, 6 * bx, "mm", reg)
    ptr8 = _gd.Rotation("br8", 0.0, 0.0, 0.3, "rad", reg)

    ptd9 = _g4.ParameterisedVolume.TubeDimensions(0.9, 2.6, 2.5, 0, "2*pi*0.9", "mm", "rad")
    ptp9 = _gd.Position("bp9", 0.0, 0.0, 8 * bx, "mm", reg)
    ptr9 = _gd.Rotation("br9", 0.0, 0.0, 0.4, "rad", reg)

    ptv = _g4.ParameterisedVolume(
        "ptv",
        tl2,
        bl1,
        9,
        [ptd1, ptd2, ptd3, ptd4, ptd5, ptd6, ptd7, ptd8, ptd9],
        [
            [ptr1, ptp1],
            [ptr2, ptp2],
            [ptr3, ptp3],
            [ptr4, ptp4],
            [ptr5, ptp5],
            [ptr6, ptp6],
            [ptr7, ptp7],
            [ptr8, ptp8],
            [ptr9, ptp9],
        ],
        reg,
    )

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T112_parameterised_tube.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(ptv)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)
    extentParam = ptv.extent()

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
