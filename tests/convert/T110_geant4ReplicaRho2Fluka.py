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
    wx = _gd.Constant("wx", 1000, reg, True)
    wy = _gd.Constant("wy", 1000, reg, True)
    wz = _gd.Constant("wz", 1000, reg, True)

    bx = _gd.Constant("bx", 100, reg, True)
    by = _gd.Constant("by", 100, reg, True)
    bz = _gd.Constant("bz", 100, reg, True)

    trmin = _gd.Constant("rmin", 100, reg, True)
    trmax = _gd.Constant("rmax", 200, reg, True)
    tz = _gd.Constant("z", 800, reg, True)
    mtdphi = _gd.Constant("mtdphi", "2*pi", reg, True)
    tdphi = _gd.Constant("tdphi", "2*pi", reg, True)
    nreplicas = _gd.Constant("nreplicas", 8, reg, True)
    tdR = _gd.Constant("tdR", trmax / nreplicas, reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.Tubs("ts", 0, trmax, tz, 0, tdphi, reg, "mm", "rad", 16, True)
    mts = _g4.solid.Tubs("mts", 0, trmax, tz, 0, mtdphi, reg, "mm", "rad", 16, True)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)
    ml = _g4.LogicalVolume(mts, wm, "ml", reg)
    mtl = _g4.ReplicaVolume(
        "mtl",
        tl,
        ml,
        _g4.ReplicaVolume.Axis.kRho,
        nreplicas,
        tdR,
        0,
        reg,
        True,
        "mm",
        "mm",
    )

    mtp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ml, "ml_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T110_geant4ReplicaRho2Fluka.gdml")

    # test __repr__
    str(mtl)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # fluka conversion
    outputFile = outputPath / "T110_geant4ReplicaRho2Fluka.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

        # flair output file
        f = _fluka.Flair(outputFile, extentBB)
        f.write(outputPath / "T110_geant4ReplicaRho2Fluka.flair")

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
