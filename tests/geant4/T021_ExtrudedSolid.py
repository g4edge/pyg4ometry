import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "150", reg, True)
    wy = _gd.Constant("wy", "150", reg, True)
    wz = _gd.Constant("wz", "150", reg, True)

    p1x = _gd.Constant("p1x", "-20", reg, True)
    p1y = _gd.Constant("p1y", "-20", reg, True)

    p2x = _gd.Constant("p2x", "-20", reg, True)
    p2y = _gd.Constant("p2y", "20", reg, True)

    p3x = _gd.Constant("p3x", "20", reg, True)
    p3y = _gd.Constant("p3y", "20", reg, True)

    p4x = _gd.Constant("p4x", "20", reg, True)
    p4y = _gd.Constant("p4y", "10", reg, True)

    p5x = _gd.Constant("p5x", "-10", reg, True)
    p5y = _gd.Constant("p5y", "10", reg, True)

    p6x = _gd.Constant("p6x", "-10", reg, True)
    p6y = _gd.Constant("p6y", "-10", reg, True)

    p7x = _gd.Constant("p7x", "20", reg, True)
    p7y = _gd.Constant("p7y", "-10", reg, True)

    p8x = _gd.Constant("p8x", "20", reg, True)
    p8y = _gd.Constant("p8y", "-20", reg, True)

    z1 = _gd.Constant("z1", "-20", reg, True)
    x1 = _gd.Constant("x1", "5", reg, True)
    y1 = _gd.Constant("y1", "5", reg, True)
    s1 = _gd.Constant("s1", "1", reg, True)

    z2 = _gd.Constant("z2", "0", reg, True)
    x2 = _gd.Constant("x2", "-5", reg, True)
    y2 = _gd.Constant("y2", "-5", reg, True)
    s2 = _gd.Constant("s2", "1", reg, True)

    z3 = _gd.Constant("z3", "20", reg, True)
    x3 = _gd.Constant("x3", "0", reg, True)
    y3 = _gd.Constant("y3", "0", reg, True)
    s3 = _gd.Constant("s3", "2", reg, True)

    polygon = [
        [p1x, p1y],
        [p2x, p2y],
        [p3x, p3y],
        [p4x, p4y],
        [p5x, p5y],
        [p6x, p6y],
        [p7x, p7y],
        [p8x, p8y],
    ]
    slices = [[z1, [x1, y1], s1], [z2, [x2, y2], s2], [z3, [x3, y3], s3]]

    polygon_float = [
        [-20, -20],
        [-20, 20],
        [20, 20],
        [20, 10],
        [-10, 10],
        [-10, -10],
        [20, -10],
        [20, -20],
    ]
    slices_float = [[-20, [5, 5], 1], [0, [-5, -5], 1], [20, [0, 0], 2]]

    polygon_float_cm = [
        [-200, -200],
        [-200, 200],
        [200, 200],
        [200, 100],
        [-100, 100],
        [-100, -100],
        [200, -100],
        [200, -200],
    ]
    slices_float_cm = [[-200, [50, 50], 1], [00, [-50, -50], 1], [200, [00, 00], 2]]

    wm = _g4.MaterialPredefined("G4_Galactic")
    xm = _g4.MaterialPredefined("G4_Fe")

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        xm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        xm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    xs = _g4.solid.ExtrudedSolid("xs", polygon, slices, reg)
    assert xs.evaluateParameterWithUnits("pPolygon") == polygon_float
    assert xs.evaluateParameterWithUnits("pZslices") == slices_float
    xs2 = _g4.solid.ExtrudedSolid("xs2", polygon, slices, reg, "cm")
    assert xs2.evaluateParameterWithUnits("pPolygon") == polygon_float_cm
    assert xs2.evaluateParameterWithUnits("pZslices") == slices_float_cm

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    xl = _g4.LogicalVolume(xs, xm, "xl", reg)
    xp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], xl, "x_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T021_ExtrudedSolid.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(xs)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
