import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    fluka=True,
    outputPath=None,
    refFilePath=None,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    px = _gd.Constant("px", "50", reg, True)
    py = _gd.Constant("py", "75", reg, True)
    pz = _gd.Constant("pz", "100", reg, True)
    pAlpha = _gd.Constant("pAlpha", "0.4", reg, True)
    pTheta = _gd.Constant("pTheta", "0.0", reg, True)
    pPhi = _gd.Constant("pPhi", "0.0", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    pm = _g4.nist_material_2geant4Material("G4_Fe")

    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    ps = _g4.solid.Para("ps", px, py, pz, pAlpha, pTheta, pPhi, reg, "mm", "rad")

    # structure
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    pp = _g4.PhysicalVolume(
        [_np.pi / 4, 0, 0],
        [0, 25, 0],
        pl,
        "pl",
        wl,
        reg,
    )

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T005_geant4Para2Fluka.gdml")

    # fluka conversion
    if not bakeTransforms:
        outputFile = outputPath / "T005_geant4Para2Fluka.inp"
    else:
        outputFile = outputPath / "T005_geant4Para2Fluka_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
