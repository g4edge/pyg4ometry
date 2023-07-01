import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi


def Test(vis = False, interactive = False, fluka = True, n_slice=16, n_stack=16) :

    # registry
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)

    ormax  = _gd.Constant("rmax","10",reg,True)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    om  = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    os = _g4.solid.Orb("os",ormax,reg,"mm", nslice=n_slice, nstack=n_stack)
        
    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ol = _g4.LogicalVolume(os, om, "ol", reg)
    op = _g4.PhysicalVolume([0,0,0],[0,0,0],  ol, "o_pv1", wl, reg)
    
    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T009_geant4Orb2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T009_geant4Orb2Fluka.inp"))

    # flair output file
    f = _fluka.Flair("T0019_geant4Orb2Fluka.inp",extentBB)
    f.write(_os.path.join(_os.path.dirname(__file__),"T009_geant4Orb2Fluka.flair"))

    if vis :
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
