import os as _os
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi


def Test(vis = False, interactive= False, fluka = True) :
    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","200",reg,True)
    wy = _gd.Constant("wy","200",reg,True)
    wz = _gd.Constant("wz","200",reg,True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    px     = _gd.Constant("px","2.5",reg,True)
    py     = _gd.Constant("py","5",reg,True)
    pz     = _gd.Constant("pz","7.5",reg,True)
    pAlpha = _gd.Constant("pAlpha","0.2",reg,True)
    pTheta = _gd.Constant("pTheta","0.4",reg,True)
    pPhi   = _gd.Constant("pPhi","0",reg,True)

    # materials
    wm  = _g4.nist_material_2geant4Material('G4_Galactic')
    pm = _g4.nist_material_2geant4Material("G4_Fe")


    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)


    pad = 4.
    nx = 2
    ny = 2
    nz = 2
    for iAlpha in range(0,nx,1) :
        dx = iAlpha * px * pad - (nx-1) * px * pad / 2.
        dAlpha = iAlpha*0.2
        for iTheta in range(0,ny,1) :
            dy = iTheta * py * 4 - (ny-1) * py * pad / 2.
            dTheta = iTheta * 0.2
            for iPhi in range(0,nz,1) :
                dz = iPhi * pz * 4 - (nz-1) * pz * pad / 2.
                dPhi = iPhi * 0.2
                # print iAlpha, iTheta, iPhi

                ps = _g4.solid.Para("ps_"+str(iAlpha)+"_"+str(iTheta)+"_"+str(iPhi),px,py,pz,dAlpha,dTheta,dPhi,reg,"mm","rad")
        
                # structure
                pl = _g4.LogicalVolume(ps, pm, "pl_"+str(iAlpha)+"_"+str(iTheta)+"_"+str(iPhi), reg)
                pp = _g4.PhysicalVolume([0,0,0],[dx,dy,dz],  pl, "p_pv1_"+str(iAlpha)+"_"+str(iTheta)+"_"+str(iPhi), wl, reg)

    # wl.clipSolid()

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent   = wl.extent(includeBoundingSolid=False)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T005_geant4Para2Fluka.gdml"))

    # fluka conversion
    if fluka :
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_os.path.join(_os.path.dirname(__file__),"T005_geant4Para2Fluka.inp"))

    # visualisation
    v = None
    if vis : 
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

if __name__ == "__main__":
    Test()
