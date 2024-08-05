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
        outputFile = "T0034_CutTubs_DefineTree.gdml"
    else:
        outputFile = _pl.Path(outputFile)

        reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    ctrmin = _gd.Constant("trmin", "2.5", reg, True)
    ctrmax = _gd.Constant("trmax", "10.0", reg, True)
    ctz = _gd.Constant("tz", "50", reg, True)
    ctstartphi = _gd.Constant("startphi", "0", reg, True)
    ctdeltaphi = _gd.Constant("deltaphi", "1.5*pi", reg, True)

    ctlowtheta = _gd.Constant("ctlowtheta", "30/360*pi", reg, True)
    ctlowphi = _gd.Constant("ctlowphi", "40/360*pi", reg, True)

    ctlowx = _gd.sin(ctlowtheta) * _gd.cos(ctlowphi)
    ctlowy = _gd.sin(ctlowtheta) * _gd.sin(ctlowphi)
    ctlowz = -_gd.cos(ctlowtheta)

    cthightheta = _gd.Constant("cthightheta", "50/360*pi", reg, True)
    cthighphi = _gd.Constant("cthighphi", "60/360*pi", reg, True)

    cthighx = _gd.sin(cthightheta) * _gd.cos(cthighphi)
    cthighy = _gd.sin(cthightheta) * _gd.sin(cthighphi)
    cthighz = _gd.cos(cthightheta)

    ctlowx.setName("ctlowx")
    ctlowy.setName("ctlowy")
    ctlowz.setName("ctlowz")

    cthighx.setName("cthighx")
    cthighy.setName("cthighy")
    cthighz.setName("cthighz")

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
