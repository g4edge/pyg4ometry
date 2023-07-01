import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np


def Test(vis = False, interactive = False, fluka = True, n_slice = 30, n_stack = 30) :

    # registry
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","200",reg,True)
    wy = _gd.Constant("wy","200",reg,True)
    wz = _gd.Constant("wz","200",reg,True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    trmin  = _gd.Constant("rmin","8.0",reg,True)
    trmax  = _gd.Constant("rmax","10.0",reg,True)
    trtor  = _gd.Constant("rtor","40.0",reg,True)
    tsphi  = _gd.Constant("sphi","0",reg,True)
    tdphi  = _gd.Constant("dphi","1.5*pi",reg,True)
    
    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    tm  = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    ts = _g4.solid.Torus("ts",trmin,trmax,trtor,tsphi,tdphi,reg,"mm","rad",nslice=n_slice,nstack=n_stack)
        
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
    w.write(_os.path.join(_os.path.dirname(__file__), "T010_geant4Torus2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T010_geant4Torus2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T010_geant4Torus2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__),"T010_geant4Torus2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
