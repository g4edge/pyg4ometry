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
    wx = _gd.Constant("wx", "2", reg, True)
    wy = _gd.Constant("wy", "2", reg, True)
    wz = _gd.Constant("wz", "2", reg, True)

    halfPi = _gd.Constant("HALPPI", "pi/2.", reg, True)
    twoPi = _gd.Constant("TWOPI", "2*pi", reg, True)
    centre = _gd.Position("centre", 0, 0, 0, "m", reg, True)
    indentity = _gd.Rotation("identity", 0, 0, 0, "rad", reg, True)
    alignSurfX = _gd.Rotation("alignSurfX", 0, halfPi, 0, "rad", reg, True)
    alignSurfY = _gd.Rotation("alignSurfY", halfPi, 0, 0, "rad", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "m")
    ts = _g4.solid.Tubs("ts", 0.1075, 0.1875, 0.1875, 0, twoPi, reg, "m", "rad")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    wa = _g4.AssemblyVolume("wa", reg, True)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)

    tp1 = _g4.PhysicalVolume(alignSurfX, [0, 0, 500], tl, "t_pv1", wa, reg)
    tp2 = _g4.PhysicalVolume(alignSurfY, [0, 0, -500], tl, "t_pv2", wa, reg)

    a_pv1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], wa, "a_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T105_assembly.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(wa)

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
