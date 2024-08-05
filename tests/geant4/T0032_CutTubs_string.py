import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
flat_ends = 2


def Test(
    vis=False, interactive=False, type=normal, outputPath=None, outputFile=None, refFilePath=None
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    if not outputFile:
        outputFile = "T0032_CutTubs_string.gdml"
    else:
        outputFile = _pl.Path(outputFile)

    reg = _g4.Registry()

    # defines
    wx = str(_gd.Constant("wx", "100", reg, True).eval())
    wy = str(_gd.Constant("wy", "100", reg, True).eval())
    wz = str(_gd.Constant("wz", "100", reg, True).eval())

    pi = str(_gd.Constant("pi", "3.1415926", reg, False).eval())
    ctrmin = str(_gd.Constant("trmin", "2.5", reg, False).eval())
    ctrmax = str(_gd.Constant("trmax", "10.0", reg, False).eval())
    ctz = str(_gd.Constant("tz", "50", reg, False).eval())
    ctstartphi = str(_gd.Constant("startphi", "0", reg, False).eval())
    ctdeltaphi = str(_gd.Constant("deltaphi", "1.5*pi", reg, False).eval())
    ctlowx = str(_gd.Constant("ctlowx", "-1", reg, False).eval())
    ctlowy = str(_gd.Constant("ctlowy", "-1", reg, False).eval())
    ctlowz = str(_gd.Constant("ctlowz", "-1", reg, False).eval())
    cthighx = str(_gd.Constant("cthighx", "1", reg, False).eval())
    cthighy = str(_gd.Constant("cthighy", "1", reg, False).eval())
    cthighz = str(_gd.Constant("cthighz", "1", reg, False).eval())

    if type == flat_ends:
        ctlowx.setExpression(0)
        ctlowy.setExpression(0)
        ctlowz.setExpression(-1)
        cthighx.setExpression(0)
        cthighy.setExpression(0)
        cthighz.setExpression(1)

    wm = _g4.Material(name="G4_Galactic")
    bm = _g4.Material(name="G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    cts = _g4.solid.CutTubs(
        "ts",
        ctrmin,
        ctrmax,
        ctz,
        ctstartphi,
        ctdeltaphi,
        [ctlowx, ctlowy, ctlowz],
        [cthighx, cthighy, cthighz],
        reg,
        "mm",
        "rad",
    )

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ctl = _g4.LogicalVolume(cts, bm, "ctl", reg)
    ctp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ctl, "ct_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / outputFile
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(cts)

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
