import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi
import numpy as _np


def Test(
    vis=False, interactive=False, fluka=True, outputPath=None, refFilePath=None, bakeTransform=False
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent
    # registry
    reg = _g4.Registry()

    # solids
    ws = _g4.solid.Box("ws", 200, 200, 200, reg, "mm")
    bs = _g4.solid.Box("b1s", 50, 75, 100, reg, "mm")

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm1 = _g4.nist_material_2geant4Material("G4_Li")
    bm2 = _g4.nist_material_2geant4Material("G4_Fe")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm1, "b1l", reg)

    bp = _g4.PhysicalVolume([0, 0, _np.pi / 4], [0, 75 / 2, 0], bl, "bp", wl, reg, scale=[1, 1, 1])

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T001_geant4Box2Fluka.gdml")

    # fluka conversion
    if not bakeTransform:
        outputFile = outputPath / "T001_geant4Box2Fluka.inp"
    else:
        outputFile = outputPath / "T001_geant4Box2Fluka_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransform)

        # fluka running
        freg.addDefaults(default="PRECISIO")
        freg.addBeam(energy=10)
        freg.addBeamPos()
        freg.addUsrBin(name="bin1")
        freg.addUsrBin(name="bin2")
        freg.addLowMatAllMaterials()
        # freg.addLowPwxs()
        freg.addRandomiz()
        freg.addStart(maxPrimHistories=100)

        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # flair output file
    f = _fluka.Flair(outputFile, extentBB)
    f.write(outputPath / "T001_geant4Box2Fluka.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
