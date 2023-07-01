import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np

normal = 1
rmin_eq_zero = 2
rmin_gt_rmax = 3

def Test(vis = False, interactive = False, fluka = True, type = normal, n_slice = 16, n_stack = 16) :

    # registry
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)
    
    pi    = _gd.Constant("pi","3.1415926",reg,True)
    hrmin = _gd.Constant("hrmin","20",reg,True)
    hrmax = _gd.Constant("hrmax","30.0",reg,True)
    hz    = _gd.Constant("hz","50.0",reg,True)
    hinst = _gd.Constant("hinst","0.7",reg,True)
    houtst= _gd.Constant("houtst","0.7",reg,True)
    
    if type == rmin_eq_zero : 
        hrmin.setExpression(0)

    if type == rmin_gt_rmax :
        hrmin.setExpression(2)
        hrmax.setExpression(1)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    hm  = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    hs = _g4.solid.Hype("ps",hrmin, hrmax, hinst, houtst, hz, reg,nslice=n_slice,nstack=n_stack)
        
    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    hl = _g4.LogicalVolume(hs, hm, "hl", reg)
    hp = _g4.PhysicalVolume([0,0,0],[0,0,0],  hl, "h_pv1", wl, reg) 
    
    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T019_geant4Hyperboloid2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T019_geant4Hyperboloid2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T019_geant4Hyperboloid2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__),"T019_geant4Hyperboloid2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
