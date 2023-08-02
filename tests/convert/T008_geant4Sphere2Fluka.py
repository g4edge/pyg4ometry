import os as _os
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka


def Test(
    vis=False, interactive=False, fluka=True, n_slice=10, n_stack=10, outputPath=None
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

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    sl = _g4.LogicalVolume(ss, sm, "sl", reg)
    sp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], sl, "s_pv1", wl, reg)

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
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / "T008_geant4Sphere2Fluka.inp")

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)


if __name__ == "__main__":
    Test()
