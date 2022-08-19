import os as _os

def OverlapCoplTest(vis = False, interactive = False) :
    import pyg4ometry.gdml as _gd
    import pyg4ometry.geant4 as _g4
    import pyg4ometry.visualisation as _vi

    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","75",reg,True)
    wy = _gd.Constant("wy","25",reg,True)
    wz = _gd.Constant("wz","25",reg,True)

    bx = _gd.Constant("bx","10",reg,True)

    b1pos = _gd.Position("b1pos",-bx,0,0,"mm",reg,True)
    b2pos = _gd.Position("b2pos",0,0,0,"mm",reg,True)
    b2pos = _gd.Position("b3pos",bx,0,0,"mm",reg,True)


    wm = _g4.MaterialPredefined("G4_Galactic") 
    bm = _g4.MaterialPredefined("G4_Fe") 

    # solids
    ws = _g4.solid.Box("ws",1.5*wx,4*wy,2.5*wz, reg, "mm")
    bs = _g4.solid.Box("bs",1.0*bx,1.0*bx,1.0*bx, reg, "mm")

    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl = _g4.LogicalVolume(bs, bm, "bl", reg)

    bp1 = _g4.PhysicalVolume([0,0,0]        ,  [-1.5*wx/2+bx/2      ,0,0],     bl, "b_pv1", wl, reg)

    bp2 = _g4.PhysicalVolume([0,0,0]        ,  [-wx/4+bx/2      ,-2*bx,0],         bl, "b_pv2", wl, reg)
    bp3 = _g4.PhysicalVolume([0,0,0]        ,  [-wx/4+bx/2+bx/2 ,-2*bx+bx/2,bx],      bl, "b_pv3", wl, reg)

    bp4 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/4-bx/2      ,-2*bx,0],         bl, "b_pv4", wl, reg)
    bp5 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/4-bx/2      ,-2*bx+bx/2,bx],      bl, "b_pv5", wl, reg)

    bp6 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/2-bx/2      ,-2*bx,0]   ,      bl, "b_pv6", wl, reg)
    bp7 = _g4.PhysicalVolume([0,0,3.14159/4],  [ wx/2-bx/2      ,-2*bx+2*bx/4,bx] ,   bl, "b_pv7", wl, reg)

    bp8 = _g4.PhysicalVolume([0,0,0]        ,  [-wx/4+bx/2      ,2*bx,0],         bl, "b_pv8", wl, reg)
    bp9 = _g4.PhysicalVolume([0,0,0]        ,  [-wx/4+bx/2+bx/2 ,2*bx+bx/2,0],      bl, "b_pv9", wl, reg)

    bp10 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/4-bx/2     ,2*bx,0],         bl, "b_pv10", wl, reg)
    bp11 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/4-bx/2     ,2*bx+bx/2,0],      bl, "b_pv11", wl, reg)

    bp12 = _g4.PhysicalVolume([0,0,0]        ,  [ wx/2-bx/2     ,2*bx,0]   ,      bl, "b_pv12", wl, reg)
    bp13 = _g4.PhysicalVolume([0,0,3.14159/4],  [ wx/2-bx/2     ,2*bx+2*bx/4,0] ,   bl, "b_pv13", wl, reg)


    bp14 = _g4.PhysicalVolume([0,0,0]        ,  [+1.5*wx/2-bx/4      ,0,0],     bl, "b_pv14", wl, reg)


    # check for overlaps
    wl.checkOverlaps(recursive = True,coplanar = True, debugIO = False)

    # set world volume
    reg.setWorld(wl.name)

    # test __repr__
    str(bs)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent   = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis : 
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume":wl, "vtkViewer":v}

if __name__ == "__main__":
    Test()
