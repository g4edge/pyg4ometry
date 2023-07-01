import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np


def Test(vis = False, interactive = False, fluka = True) :

    # registry
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)

    tx1    = _gd.Constant("tx1","20",reg,True)
    ty1    = _gd.Constant("ty1","25",reg,True)
    tx2    = _gd.Constant("tx2","5",reg,True)
    ty2    = _gd.Constant("ty2","7.5",reg,True)
    tz     = _gd.Constant("tz","10.0",reg,True)

    # materials
    wm = _g4.nist_material_2geant4Material('G4_Galactic')
    tm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    ts = _g4.solid.Trd("ts",tx1,ty1,tx2,ty2,tz,reg,"mm")
        
    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0,0,0],[0,0,0],  tl, "t_pv1", wl, reg) 
    
    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T006_geant4Trd2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T006_geant4Trd2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T006_geant4Trd2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__),"T006_geant4Trd2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
