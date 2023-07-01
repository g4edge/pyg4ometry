import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi


def Test(vis = True, interactive = False, fluka = True) :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi        = _gd.Constant("pi","3.1415926",reg,True)
    trmin = _gd.Constant("trmin", "2.5", reg, True)
    trmax = _gd.Constant("trmax", "10.0", reg, True)
    tz = _gd.Constant("tz", "50", reg, True)
    tstartphi = _gd.Constant("startphi", "0", reg, True)
    tdeltaphi = _gd.Constant("deltaphi", "1.3*pi", reg, True)
    tlowx     = _gd.Constant("ctlowx","-1",reg,True)
    tlowy     = _gd.Constant("ctlowy","-1",reg,True)
    tlowz     = _gd.Constant("ctlowz","-1",reg,True)
    thighx    = _gd.Constant("cthighx","-1",reg,True)
    thighy    = _gd.Constant("cthighy","-1",reg,True)
    thighz    = _gd.Constant("cthighz","1",reg,True)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    bm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.CutTubs("ts",trmin,trmax,tz,tstartphi,tdeltaphi,[tlowx,tlowy,tlowz],[thighx,thighy,thighz],reg,"mm","rad")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, bm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0.0, 0.0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T003_geant4CutTubs2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T003_geant4CutTubs2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T003_geant4CutTubs2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__), "T003_geant4CutTubs2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.view(interactive=interactive)

    return {'greg':reg,'freg':freg}

if __name__ == "__main__":
    Test()