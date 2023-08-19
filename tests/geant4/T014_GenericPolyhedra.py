import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


normal = 1
two_planes = 2


def Test(
    vis=False,
    interactive=False,
    type=normal,
    writeNISTMaterials=False,
    outputPath=None,
    refFilePath=None,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    pi = _gd.Constant("pi", "3.1415926", reg, True)
    psphi = _gd.Constant("sphi", "1", reg, True)
    pdphi = _gd.Constant("dphi", "4", reg, True)
    pnsid = _gd.Constant("pnsid", "4", reg, True)

    pr1 = _gd.Constant("pr1", "1", reg, True)
    pz1 = _gd.Constant("pz1", "-10", reg, True)

    pr2 = _gd.Constant("pr2", "2", reg, True)
    pz2 = _gd.Constant("pz2", "0", reg, True)

    pr3 = _gd.Constant("pr3", "1", reg, True)
    pz3 = _gd.Constant("pz3", "10", reg, True)

    pr = [pr1, pr2, pr3]
    pz = [pz1, pz2, pz3]

    if type == two_planes:
        pr = [pr1, pr2]
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
    ps = _g4.solid.GenericPolyhedra("ps", psphi, pdphi, pnsid, pr, pz, reg, "mm", "rad")
    assert ps.evaluateParameterWithUnits("pSPhi") == psphi
    assert ps.evaluateParameterWithUnits("pDPhi") == pdphi
    assert ps.evaluateParameterWithUnits("numSide") == pnsid
    if type == two_planes:
        assert ps.evaluateParameterWithUnits("pZ") == [-10, 0]
        assert ps.evaluateParameterWithUnits("pR") == [1, 2]
    else:
        assert ps.evaluateParameterWithUnits("pZ") == [-10, 0, 10]
        assert ps.evaluateParameterWithUnits("pR") == [1, 2, 1]
    ps2 = _g4.solid.GenericPolyhedra("ps2", psphi_deg, pdphi_deg, pnsid, pr, pz, reg, "cm", "deg")
    assert ps2.evaluateParameterWithUnits("pSPhi") == psphi
    assert ps2.evaluateParameterWithUnits("pDPhi") == pdphi
    assert ps2.evaluateParameterWithUnits("numSide") == pnsid
    if type == two_planes:
        assert ps2.evaluateParameterWithUnits("pZ") == [-100, 0]
        assert ps2.evaluateParameterWithUnits("pR") == [10, 20]
    else:
        assert ps2.evaluateParameterWithUnits("pZ") == [-100, 0, 100]
        assert ps2.evaluateParameterWithUnits("pR") == [10, 20, 10]

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T014_GenericPolyhedra.gdml"
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
