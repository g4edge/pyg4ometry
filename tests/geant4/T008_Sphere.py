import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    n_slice=10,
    n_stack=10,
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

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    srmin = _gd.Constant("rmin", "8", reg, True)
    srmax = _gd.Constant("rmax", "10", reg, True)
    ssphi = _gd.Constant("sphi", "0", reg, True)
    # sdphi  = _gd.Constant("dphi","2*pi",reg,True)
    sdphi = _gd.Constant("dphi", "1.75*pi", reg, True)
    sstheta = _gd.Constant("stheta", "0", reg, True)
    sdtheta = _gd.Constant("dtheta", "0.75*pi", reg, True)
    # sdtheta = _gd.Constant("dtheta", "pi", reg, True)

    ssphi_deg = _gd.Constant("sphi_deg", "0", reg, True)
    # sdphi_deg  = _gd.Constant("dphi_deg","360",reg,True)
    sdphi_deg = _gd.Constant("dphi_deg", "315", reg, True)
    sstheta_deg = _gd.Constant("stheta_deg", "0", reg, True)
    sdtheta_deg = _gd.Constant("dtheta_deg", "135", reg, True)
    # sdtheta_deg = _gd.Constant("dtheta_deg", "180", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    sm = _g4.MaterialPredefined("G4_Fe")
    # materials
    if writeNISTMaterials:
        wm = _g4.nist_material_2geant4Material("G4_Galactic", reg)
        sm = _g4.nist_material_2geant4Material("G4_Au", reg)
    else:
        wm = _g4.MaterialPredefined("G4_Galactic")
        sm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ss = _g4.solid.Sphere(
        "ss",
        srmin,
        srmax,
        ssphi,
        sdphi,
        sstheta,
        sdtheta,
        reg,
        "mm",
        "rad",
        nslice=n_slice,
        nstack=n_stack,
    )

    assert ss.evaluateParameterWithUnits("pRmin") == srmin
    assert ss.evaluateParameterWithUnits("pRmax") == srmax
    assert ss.evaluateParameterWithUnits("pSPhi") == ssphi
    assert ss.evaluateParameterWithUnits("pDPhi") == sdphi
    assert ss.evaluateParameterWithUnits("pSTheta") == sstheta
    assert ss.evaluateParameterWithUnits("pDTheta") == sdtheta
    ss2 = _g4.solid.Sphere(
        "ss2",
        srmin,
        srmax,
        ssphi_deg,
        sdphi_deg,
        sstheta_deg,
        sdtheta_deg,
        reg,
        "cm",
        "deg",
        nslice=n_slice,
        nstack=n_stack,
    )
    assert ss2.evaluateParameterWithUnits("pRmin") == 10 * srmin
    assert ss2.evaluateParameterWithUnits("pRmax") == 10 * srmax
    assert ss2.evaluateParameterWithUnits("pSPhi") == ssphi
    assert ss2.evaluateParameterWithUnits("pDPhi") == sdphi
    assert ss2.evaluateParameterWithUnits("pSTheta") == sstheta
    assert ss2.evaluateParameterWithUnits("pDTheta") == sdtheta

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    sl = _g4.LogicalVolume(ss, sm, "sl", reg)
    sp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], sl, "s_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    outputFile = outputPath / "T008_Sphere.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # test __repr__
    str(ss)

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
