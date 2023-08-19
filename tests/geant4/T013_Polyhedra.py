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
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    psphi = _gd.Constant("sphi", "1", reg, True)
    pdphi = _gd.Constant("dphi", "4", reg, True)
    pnsid = _gd.Constant("pnsid", "4", reg, True)

    prmin1 = _gd.Constant("prmin1", "1", reg, True)
    prmax1 = _gd.Constant("prmax1", "9", reg, True)
    pz1 = _gd.Constant("z1", "-10", reg, True)

    prmin2 = _gd.Constant("prmin2", "3", reg, True)
    prmax2 = _gd.Constant("prmax2", "5", reg, True)
    pz2 = _gd.Constant("z2", "12", reg, True)

    prmin = [prmin1, prmin2]
    prmax = [prmax1, prmax2]
    pz = [pz1, pz2]

    psphi_deg = _gd.Constant("sphi_deg", "1/pi*180", reg, True)
    pdphi_deg = _gd.Constant("dphi_deg", "4/pi*180", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    pm = _g4.MaterialPredefined("G4_Fe")

    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        pm = _g4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        pm = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.Polyhedra("ps", psphi, pdphi, pnsid, len(pz), pz, prmin, prmax, reg, "mm", "rad")
    assert ps.evaluateParameterWithUnits("pSPhi") == psphi
    assert ps.evaluateParameterWithUnits("pDPhi") == pdphi
    assert ps.evaluateParameterWithUnits("numSide") == pnsid
    assert ps.evaluateParameterWithUnits("numZPlanes") == len(pz)
    assert ps.evaluateParameterWithUnits("zPlane") == [-10, 12]
    assert ps.evaluateParameterWithUnits("rInner") == [1, 3]
    assert ps.evaluateParameterWithUnits("rOuter") == [9, 5]
    ps2 = _g4.solid.Polyhedra(
        "ps2", psphi_deg, pdphi_deg, pnsid, len(pz), pz, prmin, prmax, reg, "cm", "deg"
    )
    assert ps2.evaluateParameterWithUnits("pSPhi") == psphi
    assert ps2.evaluateParameterWithUnits("pDPhi") == pdphi
    assert ps2.evaluateParameterWithUnits("numSide") == pnsid
    assert ps2.evaluateParameterWithUnits("numZPlanes") == len(pz)
    assert ps2.evaluateParameterWithUnits("zPlane") == [-100, 120]
    assert ps2.evaluateParameterWithUnits("rInner") == [10, 30]
    assert ps2.evaluateParameterWithUnits("rOuter") == [90, 50]

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T013_Polyhedra.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)

    # test __repr__
    str(ps)

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
