import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.misc as _mi


def Test_OpticalSurface(outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # World box
    wx = _gd.Constant("wx", "150", reg, True)
    wy = _gd.Constant("wy", "150", reg, True)
    wz = _gd.Constant("wz", "150", reg, True)

    # Outer big box
    ox = _gd.Constant("ox", "100", reg, True)
    oy = _gd.Constant("oy", "100", reg, True)
    oz = _gd.Constant("oz", "100", reg, True)

    # Water tank
    tx = _gd.Constant("tx", "50", reg, True)
    ty = _gd.Constant("ty", "50", reg, True)
    tz = _gd.Constant("tz", "50", reg, True)

    # Air bubble
    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic")

    ne = _g4.ElementSimple("Nitrogen", "N", 7, 14.01)
    he = _g4.ElementSimple("Hydrogen", "H", 1, 1.01)
    oe = _g4.ElementSimple("Oxygen", "O", 8, 16.0)

    air = _g4.MaterialCompound("Air", 1.290e-3, 2, reg)
    air.add_element_massfraction(ne, 0.7)
    air.add_element_massfraction(oe, 0.3)
    air.addVecProperty("RINDEX", [2.034e-03, 2.068e-03, 2.103e-03, 2.139e-03], [1, 1, 1, 1])

    water = _g4.MaterialCompound("Water", 1.0, 2, reg)
    water.add_element_massfraction(he, 0.112)
    water.add_element_massfraction(oe, 0.888)
    water.addVecProperty(
        "RINDEX",
        [2.034e-03, 2.068e-03, 2.103e-03, 2.139e-03],
        [1.3435, 1.344, 1.3445, 1.345],
    )
    water.addVecProperty(
        "ABSLENGTH",
        [2.034e-03, 2.068e-03, 2.103e-03, 2.139e-03],
        [3448, 4082, 6329, 9174],
        vunit="m",
    )
    water.addConstProperty("YIELDRATIO", 0.8)

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bigbox = _g4.solid.Box("bigbox", ox, oy, oz, reg, "mm")
    tank = _g4.solid.Box("tank", tx, ty, tz, reg, "mm")
    bubble = _g4.solid.Box("bubble", bx, by, bz, reg, "mm")

    opa = _g4.solid.OpticalSurface(
        "AirSurface", finish="0", model="0", surf_type="1", value="1", registry=reg
    )
    opw = _g4.solid.OpticalSurface(
        "WaterSurface", finish="3", model="1", surf_type="1", value="0", registry=reg
    )

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ol = _g4.LogicalVolume(bigbox, wm, "bigbox_logical", reg)
    tl = _g4.LogicalVolume(tank, water, "tank_logical", reg)
    bl = _g4.LogicalVolume(bubble, air, "bubble_logical", reg)
    op = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ol, "bigbox_pv", wl, reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "tank_pv1", ol, reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 2.5, 0], bl, "bubble_pv1", tl, reg)
    _g4.SkinSurface("AirSurface", bl, opa, reg)
    _g4.BorderSurface("WaterSurface", bp, op, opw, reg)

    #######################################################################################

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T202_Optical.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)


if __name__ == "__main__":
    Test_OpticalSurface()
