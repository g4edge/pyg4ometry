import pyg4ometry.gdml as _gdml
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vis
import pyg4ometry.misc as _misc

import pathlib as _pl


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # all solids?
    # logical, assembly
    # booleans, union, difference, intersection
    # division , replica, parameterisation

    reg = _g4.Registry()

    # defines
    wx = _gdml.Constant("wx", "100", reg, True)
    wy = _gdml.Constant("wy", "100", reg, True)
    wz = _gdml.Constant("wz", "100", reg, True)

    bx = _gdml.Constant("bx", "10", reg, True)
    by = _gdml.Constant("by", "10", reg, True)
    bz = _gdml.Constant("bz", "10", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Au")

    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")

    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T050_Everything.gdml"
    w = _gdml.Writer()
    w.addDetector(reg)
    w.write(outputFile)
