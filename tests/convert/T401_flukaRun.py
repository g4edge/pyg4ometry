import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi
import numpy as _np


def Test(vis=False, interactive=False, fluka=True, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # solids
    ws = _g4.solid.Box("ws", 5000, 5000, 50000, reg, "mm")

    q_len = 250
    d_len = 5000
    b_len = 2000

    qs = _g4.solid.Box("qs", 750, 750, q_len, reg, "mm")
    ds = _g4.solid.Box("ds", 500, 500, d_len, reg, "mm")
    bs = _g4.solid.Tubs("bs", 20, 25, b_len, 0, _np.pi * 2, reg, lunit="mm", aunit="rad")

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    qm = _g4.nist_material_2geant4Material("G4_Galactic")
    dm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ql = _g4.LogicalVolume(qs, qm, "ql", reg)
    dl = _g4.LogicalVolume(ds, dm, "dm", reg)
    bl = _g4.LogicalVolume(bs, bm, "bm", reg)

    s = b_len / 2
    bp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, s], bl, "bp1", wl, reg)
    s += b_len / 2 + q_len / 2
    qp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, s], ql, "qp1", wl, reg)
    s += q_len / 2 + b_len / 2
    bp2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, s], bl, "bp2", wl, reg)
    s += d_len / 2 + b_len / 2
    dp1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, s], dl, "dp1", wl, reg)
    s += d_len / 2 + b_len / 2
    dp3 = _g4.PhysicalVolume([0, 0, 0], [0, 0, s], bl, "bp3", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T401_flukaRun.gdml")

    vbase = _vi.ViewerBase()
    vbase.addLogicalVolume(wl)

    # fluka conversion
    outputFile = outputPath / "T401_flukaRun.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)

        # fluka running
        freg.addDefaults(default="PRECISIO")
        freg.addBeam(energy=1, particleType="ELECTRON")
        freg.addBeamPos()
        freg.addUsrBin(name="bin1")
        freg.addUsrBin(name="bin2")
        freg.addUsrBdx(
            1,
            0,
            1,
            "ALL-PART",
            freg.PhysVolToRegionMap["wl"],
            freg.PhysVolToRegionMap["qp1"],
            "qp1_all_part",
            area=1,
            minKE=0.1,
            maxKE=1.0,
            nKEbin=100,
            minSA=0,
            maxSA=4 * 3.14159,
            nSAbin=100,
        )
        freg.addLowMatAllMaterials()
        freg.addUsrDump(mgdraw=100, lun=23, mgdrawOpt=-1)
        freg.addRandomiz()
        freg.addStart(maxPrimHistories=1000)

        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"greg": reg, "freg": freg, "vbase": vbase}


if __name__ == "__main__":
    Test()
