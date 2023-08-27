import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def MakeGeometry():
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", 250, reg, True)
    wy = _gd.Constant("wy", 250, reg, True)
    wz = _gd.Constant("wz", 250, reg, True)

    bx = _gd.Constant("bx", 40, reg, True)
    by = _gd.Constant("by", 20, reg, True)
    bz = _gd.Constant("bz", 1, reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Si")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)

    al = _g4.AssemblyVolume("al", reg)
    bp1 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, -35, 0, "mm"], bl, "b_pv1", al, reg)
    bp2 = _g4.PhysicalVolume([0, 0, 90, "deg"], [35, 0, 0, "mm"], bl, "b_pv2", al, reg)
    bp3 = _g4.PhysicalVolume([0, 0, 180, "deg"], [0, 35, 0, "mm"], bl, "b_pv3", al, reg)
    bp4 = _g4.PhysicalVolume([0, 0, 270, "deg"], [-35, 0, 0, "mm"], bl, "b_pv4", al, reg)

    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ap1 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, 0, -100, "mm"], al, "a_pv1", wl, reg)
    ap2 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, 0, -50, "mm"], al, "a_pv2", wl, reg)
    ap3 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, 0, 0, "mm"], al, "a_pv3", wl, reg)
    ap4 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, 0, 50, "mm"], al, "a_pv4", wl, reg)
    ap5 = _g4.PhysicalVolume([0, 0, 0, "deg"], [0, 0, 100, "mm"], al, "a_pv5", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    return reg


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg0 = MakeGeometry()
    wl = reg0.getWorldVolume()

    reg1 = _g4.Registry()
    reg1.addVolumeRecursive(wl, collapseAssemblies=True)
    reg1.setWorld(wl)

    # check assembly collapse has produced correct results
    assert len(wl.daughterVolumes) == 20
    for i in range(1, 5, 1):
        for j in range(1, 4, 1):
            pvname = f"a_pv{i}_b_pv{j}"
            assert pvname in wl._daughterVolumesDict
            pv = wl._daughterVolumesDict[pvname]
            assert round(float(pv.rotation[2]), 6) == round((j - 1) * 90 * _gd.Units.unit("deg"), 6)
            assert round(float(pv.position[2]), 1) == round((i - 3) * 50 * _gd.Units.unit("mm"), 1)

    # check for overlaps
    wl.checkOverlaps(recursive=True, coplanar=False)

    # gdml output
    outputFile = outputPath / "T434_MergeRegistry_CollapseAssembly.gdml"
    w = _gd.Writer()
    w.addDetector(reg1)
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

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
