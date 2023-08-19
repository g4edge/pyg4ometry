import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def MakeGeometry(size=50, lowOxygen=False):
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", size, reg, True)
    wy = _gd.Constant("wy", size, reg, True)
    wz = _gd.Constant("wz", size, reg, True)

    # "size" argument allows us to define different sizes with the same name
    # to test resolution when we merge
    bx = _gd.Constant("bx", size / 5, reg, True)
    by = _gd.Constant("by", size / 5, reg, True)
    bz = _gd.Constant("bz", size / 5, reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")

    # this allows us to define two technically different materials but called
    # "air" so they should be resolved correctly in the merging
    air = _g4.MaterialCompound("air", 1.290e-3, 2, reg)
    oe = _g4.ElementSimple("oxygen", "O", 8, 16.0)
    if lowOxygen:
        ne = _g4.ElementSimple("nitrogen", "N", 7, 15.01)
        air.add_element_massfraction(ne, 0.95)
        air.add_element_massfraction(oe, 0.05)
    else:
        ne = _g4.ElementSimple("nitrogen", "N", 7, 14.01)
        air.add_element_massfraction(ne, 0.7)
        air.add_element_massfraction(oe, 0.3)

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, air, "bl", reg)

    scale = _gd.Defines.Scale("sca_reflection", 1, 1, -1, registry=reg)

    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg, scale=scale)

    # set world volume
    reg.setWorld(wl.name)

    return reg


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg0 = _g4.Registry()
    reg1 = MakeGeometry()
    reg2 = MakeGeometry(size=70, lowOxygen=True)
    reg3 = MakeGeometry(size=100, lowOxygen=True)

    l1 = reg1.getWorldVolume()
    l2 = reg2.getWorldVolume()
    l3 = reg3.getWorldVolume()

    wx0 = _gd.Constant("wx0", "400", reg0, True)
    wy0 = _gd.Constant("wy0", "400", reg0, True)
    wz0 = _gd.Constant("wz0", "400", reg0, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    ws = _g4.solid.Box("ws", wx0, wy0, wz0, reg0, "mm")
    wl = _g4.LogicalVolume(ws, wm, "wl", reg0)

    p1 = _g4.PhysicalVolume([0, 0, 0], [-50, 0, 0], l1, "l1_pv", wl, reg0)
    p2 = _g4.PhysicalVolume([0, 0, 0], [50, 0, 0], l2, "l2_pv", wl, reg0)
    p3 = _g4.PhysicalVolume([0, 0, 0], [150, 0, 0], l3, "l3_pv", wl, reg0)

    reg0.addVolumeRecursive(p1)
    reg0.addVolumeRecursive(p2)
    reg0.addVolumeRecursive(p3)

    reg0.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T400_MergeRegistry.gdml"
    w = _gd.Writer()
    w.addDetector(reg0)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg0.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"teststatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
