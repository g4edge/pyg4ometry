import os as _os

def BoxTest(vis = False, interactive = False, writeNISTMaterials = False) :
    import pyg4ometry.gdml as _gd
    import pyg4ometry.geant4 as _g4
    import pyg4ometry.visualisation as _vi
    import pyg4ometry.convert as _conv
    import pyg4ometry.fluka as _flu

    reg = _g4.Registry()
    
    # defines 
    wx = _gd.Constant("wx","100",reg,True)
    wy = _gd.Constant("wy","100",reg,True)
    wz = _gd.Constant("wz","100",reg,True)

    bx = _gd.Constant("bx","10",reg,True)
    by = _gd.Constant("by","10",reg,True)
    bz = _gd.Constant("bz","10",reg,True)

    # materials
    if writeNISTMaterials :
        wm = _g4.nist_material_2geant4Material("G4_Galactic",reg)
        bm = _g4.nist_material_2geant4Material("G4_Au",reg)
    else :
        wm = _g4.MaterialPredefined("G4_Galactic")
        bm = _g4.MaterialPredefined("G4_Au")

    # solids
    ws = _g4.solid.Box("ws",wx,wy,wz, reg, "mm")
    bs = _g4.solid.Box("bs",bx,by,bz, reg, "mm")
    assert(bs.evaluateParameterWithUnits('pX') == bx)
    assert(bs.evaluateParameterWithUnits('pY') == by)
    assert(bs.evaluateParameterWithUnits('pZ') == bz)
    bs2 = _g4.solid.Box("bs2",bx,by,bz, reg, "cm")
    assert(bs2.evaluateParameterWithUnits('pX') == 10*bx)
    assert(bs2.evaluateParameterWithUnits('pY') == 10*by)
    assert(bs2.evaluateParameterWithUnits('pZ') == 10*bz)
        
    # structure 
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0,0,0],[0,0,0],  bl, "b_pv1", wl, reg) 
    
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
        v = _vi.PubViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)


    return {"testStatus": True, "logicalVolume":wl, "vtkViewer":v, "registry":reg}

if __name__ == "__main__":
    Test()
