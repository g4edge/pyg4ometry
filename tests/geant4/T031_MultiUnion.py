import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import random as _rand
import numpy as _np
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, writeNISTMaterials=False, outputPath=None, refFilePath=None):
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
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        bm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        bm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "cm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "cm")

    _rand.seed(1234567890)

    nbox = 15
    solids = []
    transforms = []
    for i in range(0, nbox, 1):
        r = 2 * bx.eval() * _rand.uniform(0, 1)
        t = _np.pi * _rand.uniform(0, 1)
        p = 2 * _np.pi * _rand.uniform(0, 1)
        x = r * _np.sin(t) * _np.cos(p)
        y = r * _np.sin(t) * _np.sin(p)
        z = r * _np.cos(t)
        solids.append(bs)
        transforms.append([[0, t, p], [x, y, z, "cm"]])

    mu = _g4.solid.MultiUnion("mu", solids, transforms, reg, True)
    mu_trans = mu.evaluateParameterWithUnits("transformations")
    for i in range(0, nbox, 1):
        for j in range(0, 2, 1):
            for k in range(0, 3, 1):
                assert round(mu_trans[i][j][k], 6) == round((10.0**j) * transforms[i][j][k], 6)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(mu, bm, "ml", reg)
    mp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "m_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T031_MultiUnion.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(mu)

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

    return {"teststatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
