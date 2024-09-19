import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
zcut_outofrange = 2


def Test(
    vis=False,
    interactive=False,
    fluka=True,
    type=normal,
    n_slice=16,
    outputPath=None,
    refFilePath=None,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "200", reg, True)
    wy = _gd.Constant("wy", "200", reg, True)
    wz = _gd.Constant("wz", "200", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    edx = _gd.Constant("eax", "0.5", reg, True)
    edy = _gd.Constant("eby", "1", reg, True)
    ezmax = _gd.Constant("ecz", "40", reg, True)
    ezcut = _gd.Constant("ebc", "20", reg, True)

    if type == zcut_outofrange:
        ezcut.setExpression(30)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    em = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    es = _g4.solid.EllipticalCone("es", edx, edy, ezmax, ezcut, reg, "mm", nslice=n_slice)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    el = _g4.LogicalVolume(es, em, "el", reg)
    ep = _g4.PhysicalVolume([_np.pi / 4, 0, 0], [0, 15, 0], el, "e_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T017_geant4EllipticalCone2Fluka.gdml")

    # fluka conversion
    if not bakeTransforms:
        outputFile = outputPath / "T017_geant4EllipticalCone2Fluka.inp"
    else:
        outputFile = outputPath / "T017_geant4EllipticalCone2Fluka_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # flair output file
    f = _fluka.Flair(outputFile, extentBB)
    f.write(str(outputPath / "T017_geant4EllipticalCone2Fluka.flair"))

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
