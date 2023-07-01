import os as _os
import numpy as _np
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi

normal         = 1
r1min_gt_r1max = 2
r2min_gt_r2max = 3
dphi_gt_2pi    = 4
dphi_eq_2pi    = 5 
cone_up        = 6
inner_cylinder = 7

def Test(vis = False, interactive = False, fluka = True, type = normal) :
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    crmin1 = _gd.Constant("crmin1","6",reg,True)
    crmax1 = _gd.Constant("crmax1","20",reg,True)
    crmin2 = _gd.Constant("crmin2","5",reg,True)
    crmax2 = _gd.Constant("crmax2","10",reg,True)
    cz     = _gd.Constant("cz","100",reg,True)
    cdp    = _gd.Constant("cdp","1.2*pi",reg,True)
    zero   = _gd.Constant("zero","0.0",reg,False)

    if type == r1min_gt_r1max : 
        crmin1.setExpression(21)
    elif type == type == r2min_gt_r2max : 
        crmin2.setExpression(11)
    elif type == dphi_gt_2pi : 
        cdp.setExpression("3*pi")
    elif type == dphi_eq_2pi : 
        cdp.setExpression(2*_np.pi)
    elif type == cone_up : 
        crmin1.setExpression(5)
        crmax1.setExpression(10)
        crmin2.setExpression(6)
        crmax2.setExpression(20)
    elif type == inner_cylinder :
        crmin1.setExpression(5)
        crmin2.setExpression(5)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    cm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    cs = _g4.solid.Cons("cs",crmin1,crmax1,crmin2,crmax2,cz,zero,cdp,reg,"mm")
        
    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    cl = _g4.LogicalVolume(cs, cm, "cl", reg)
    cp = _g4.PhysicalVolume([0,0,0],[0,0,0],  cl, "c_pv1", wl, reg) 
    
    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)


    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T004_geant4Cons2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T004_geant4Cons2Fluka.inp"))

    # visualisation
    v = None
    if vis : 
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

if __name__ == "__main__":
    Test()
