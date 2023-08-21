import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, fluka=True, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "1000", reg, True)
    wy = _gd.Constant("wy", "1000", reg, True)
    wz = _gd.Constant("wz", "1000", reg, True)

    bx = _gd.Constant("bx", "100", reg, True)
    by = _gd.Constant("by", "100", reg, True)
    bz = _gd.Constant("bz", "100", reg, True)

    mbx = _gd.Constant("mbx", "800", reg, True)
    mby = _gd.Constant("mby", "100", reg, True)
    mbz = _gd.Constant("mbz", "100", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    mbs = _g4.solid.Box("mbs", mbx, mby, mbz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    ml = _g4.LogicalVolume(mbs, wm, "ml", reg)
    mbl = _g4.ReplicaVolume(
        "mbl", bl, ml, _g4.ReplicaVolume.Axis.kXAxis, 8, 100, 0, reg, True, "mm", "mm"
    )

    mbp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ml, "ml_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T106_geant4ReplicaX2Fluka.gdml")

    # test __repr__
    str(mbl)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # fluka conversion
    outputFile = outputPath / "T106_geant4ReplicaX2Fluka.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

        # flair output file
        f = _fluka.Flair(outputFile, extentBB)
        f.write(outputPath / "T106_geant4ReplicaX2Fluka.flair")

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
