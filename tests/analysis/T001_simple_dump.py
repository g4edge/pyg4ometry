import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi


def Test(vis=True, interactive=False, fluka=True, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "1000", reg, True)
    wy = _gd.Constant("wy", "1000", reg, True)
    wz = _gd.Constant("wz", "1000", reg, True)

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    db = _g4.solid.Box("db", 700, 700, 700, reg, "mm")
    dt = _g4.solid.Tubs("dt", 0, 100, 500, 0, _np.pi * 2, reg, "mm", "rad")

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")
    tm = _g4.nist_material_2geant4Material("G4_C")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(db, bm, "bl", reg)
    tl = _g4.LogicalVolume(dt, tm, "tl", reg)
    bp = _g4.PhysicalVolume([0, 0.0, 0.0], [0, 0, 0], bl, "bl1", wl, reg)
    tp = _g4.PhysicalVolume([0, 0.0, 0.0], [0, 0, 100], tl, "tl1", bl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T001_simple_dump.gdml")

    # fluka conversion
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()

        freg.addDefaults(default="PRECISIO")
        freg.addBeam(energy=100)
        freg.addBeamPos()
        freg.addUsrBin(
            name="bin1",
            e1max=100,
            e2max=100,
            e3max=100,
            e1min=-100,
            e2min=-100,
            e3min=-100,
            e1nbin=100,
            e2nbin=100,
            e3nbin=100,
        )
        freg.addLowMatAllMaterials()
        # freg.addLowPwxs()
        freg.addRandomiz()
        freg.addStart(maxPrimHistories=1000)

        w.addDetector(freg)
        w.write(outputPath / "T001_simple_dump.inp")

    # flair output file
    f = _fluka.Flair("T001_simple_dump.inp", extentBB)
    f.write(outputPath / "T001_simple_dump.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.view(interactive=interactive)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
