import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pathlib as _pl
import pyg4ometry.misc as _mi

normal = 1
non_intersecting = 2


def Test(vis=False, interactive=False, fluka=True, type=normal, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")
    if type == normal:
        ns = _g4.solid.Intersection("ns", bs, bs, [[0.1, 0.2, 0.3], [bx / 2, by / 2, bz / 2]], reg)
    elif type == non_intersecting:
        ns = _g4.solid.Intersection("ns", bs, bs, [[0.1, 0.2, 0.3], [bx * 2, by * 2, bz * 22]], reg)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    nl = _g4.LogicalVolume(ns, bm, "nl", reg)
    np = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], nl, "i_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    outputFile = outputPath / "T030_geant4Intersection2Fluka.inp"
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
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
