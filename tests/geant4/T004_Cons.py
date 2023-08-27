import os as _os
import pathlib as _pl
import numpy as _np
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
r1min_gt_r1max = 2
r2min_gt_r2max = 3
dphi_gt_2pi = 4
dphi_eq_2pi = 5
cone_up = 6
inner_cylinder = 7


def Test(
    vis=False,
    interactive=False,
    type=normal,
    n_slice=10,
    writeNISTMaterials=False,
    outputPath=None,
    outputFile=None,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    if not outputFile:
        outputFile = "T004_Cons.gdml"
    else:
        outputFile = _pl.Path(outputFile)

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    crmin1 = _gd.Constant("crmin1", "6", reg, True)
    crmax1 = _gd.Constant("crmax1", "20", reg, True)
    crmin2 = _gd.Constant("crmin2", "5", reg, True)
    crmax2 = _gd.Constant("crmax2", "10", reg, True)
    cz = _gd.Constant("cz", "100", reg, True)
    cdp = _gd.Constant("cdp", "1.5*pi", reg, True)
    zero = _gd.Constant("zero", "0.0", reg, False)

    cdp_deg = _gd.Constant("cdp_deg", "270", reg, True)

    if type == r1min_gt_r1max:
        crmin1.setExpression(21)
    elif type == type == r2min_gt_r2max:
        crmin2.setExpression(11)
    elif type == dphi_gt_2pi:
        cdp.setExpression("3*pi")
        cdp_deg.setExpression("540")
    elif type == dphi_eq_2pi:
        cdp.setExpression(2 * _np.pi)
        cdp_deg.setExpression("360")
    elif type == cone_up:
        crmin1.setExpression(5)
        crmax1.setExpression(10)
        crmin2.setExpression(6)
        crmax2.setExpression(20)
    elif type == inner_cylinder:
        crmin1.setExpression(5)
        crmin2.setExpression(5)

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        cm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        cm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    cs = _g4.solid.Cons(
        "cs",
        crmin1,
        crmax1,
        crmin2,
        crmax2,
        cz,
        zero,
        cdp,
        reg,
        "mm",
        "rad",
        nslice=n_slice,
    )
    assert cs.evaluateParameterWithUnits("pRmin1") == crmin1
    assert cs.evaluateParameterWithUnits("pRmin2") == crmin2
    assert cs.evaluateParameterWithUnits("pRmax1") == crmax1
    assert cs.evaluateParameterWithUnits("pRmax2") == crmax2
    assert cs.evaluateParameterWithUnits("pDz") == cz
    assert cs.evaluateParameterWithUnits("pSPhi") == zero
    assert cs.evaluateParameterWithUnits("pDPhi") == cdp
    assert cs.evaluateParameterWithUnits("nslice") == n_slice
    cs2 = _g4.solid.Cons(
        "cs2",
        crmin1,
        crmax1,
        crmin2,
        crmax2,
        cz,
        zero,
        cdp_deg,
        reg,
        "cm",
        "deg",
        nslice=n_slice,
    )
    assert cs2.evaluateParameterWithUnits("pRmin1") == 10 * crmin1
    assert cs2.evaluateParameterWithUnits("pRmin2") == 10 * crmin2
    assert cs2.evaluateParameterWithUnits("pRmax1") == 10 * crmax1
    assert cs2.evaluateParameterWithUnits("pRmax2") == 10 * crmax2
    assert cs2.evaluateParameterWithUnits("pDz") == 10 * cz
    assert cs2.evaluateParameterWithUnits("pSPhi") == zero
    assert cs2.evaluateParameterWithUnits("pDPhi") == cdp
    assert cs2.evaluateParameterWithUnits("nslice") == n_slice

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    cl = _g4.LogicalVolume(cs, cm, "cl", reg)
    cp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], cl, "c_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / outputFile
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(cs)

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
