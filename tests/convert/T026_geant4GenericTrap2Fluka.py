import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np

normal = 1
zero_area_quad = 2

def Test(vis = False, interactive = False, fluka = True) :

    # registry
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)

    # pi    = _gd.Constant("pi","3.1415926",reg,True)

    tv1x  = _gd.Constant("v1x","10",reg,True)
    tv1y  = _gd.Constant("v1y","10",reg,True)

    tv2x  = _gd.Constant("v2x","20",reg,True)
    tv2y  = _gd.Constant("v2y","30",reg,True)

    tv3x  = _gd.Constant("v3x","30",reg,True)
    tv3y  = _gd.Constant("v3y","30",reg,True)

    tv4x  = _gd.Constant("v4x","40",reg,True)
    tv4y  = _gd.Constant("v4y","10",reg,True)

    tv5x  = _gd.Constant("v5x","20",reg,True)
    tv5y  = _gd.Constant("v5y","20",reg,True)

    tv6x  = _gd.Constant("v6x","20",reg,True)
    tv6y  = _gd.Constant("v6y","40",reg,True)

    tv7x  = _gd.Constant("v7x","40",reg,True)
    tv7y  = _gd.Constant("v7y","40",reg,True)

    tv8x  = _gd.Constant("v8x","40",reg,True)
    tv8y  = _gd.Constant("v8y","20",reg,True)
    
    tz    = _gd.Constant("z","30",reg,True)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    tm  = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    ts = _g4.solid.GenericTrap("ts",tv1x,tv1y,tv2x,tv2y,tv3x,tv3y,tv4x,tv4y,tv5x,tv5y,
                               tv6x,tv6y,tv7x,tv7y,tv8x,tv8y,tz,reg)
        
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
    w.write(_os.path.join(_os.path.dirname(__file__), "T026_geant4GenericTrap2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T026_geant4GenericTrap2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T026_geant4GenericTrap2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__),"T026_geant4GenericTrap2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
