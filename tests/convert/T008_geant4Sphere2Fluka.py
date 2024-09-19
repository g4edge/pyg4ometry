import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.misc as _mi


def Test(
    vis=False,
    interactive=False,
    fluka=True,
    n_slice=10,
    n_stack=10,
    outputPath=None,
    refFilePath=None,
    cuts=False,
    bakeTransforms=False,
):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi    = _gd.Constant("pi","3.1415926",reg,True)
    srmin = _gd.Constant("rmin", "8", reg, True)
    srmax = _gd.Constant("rmax", "10", reg, True)
    ssphi = _gd.Constant("sphi", "0.1", reg, True)
    sdphi = _gd.Constant("dphi", "0.8*pi", reg, True)
    sstheta = _gd.Constant("stheta", "0.0*pi", reg, True)
    sdtheta = _gd.Constant("dtheta", "1.0*pi", reg, True)

    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    sm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    if cuts:
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
    else:
        ss = _g4.solid.Sphere(
            "ss",
            0,
            srmax,
            0,
            2 * _np.pi,
            0,
            _np.pi,
            reg,
            "mm",
            "rad",
            nslice=n_slice,
            nstack=n_stack,
        )
    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    sl = _g4.LogicalVolume(ss, sm, "sl", reg)
    sp = _g4.PhysicalVolume([_np.pi / 4, 0, 0], [0, 20, 0], sl, "s_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T008_geant4Sphere2Fluka.gdml")

    # fluka conversion
    if not cuts and not bakeTransforms:
        outputFile = outputPath / "T008_geant4Sphere2Fluka.inp"
    elif cuts and not bakeTransforms:
        outputFile = outputPath / "T008_geant4Sphere2Fluka_cuts.inp"
    elif not cuts and bakeTransforms:
        outputFile = outputPath / "T008_geant4Sphere2Fluka_baked.inp"
    elif cuts and bakeTransforms:
        outputFile = outputPath / "T008_geant4Sphere2Fluka_cuts_baked.inp"

    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg, bakeTransforms=bakeTransforms)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputFile)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
