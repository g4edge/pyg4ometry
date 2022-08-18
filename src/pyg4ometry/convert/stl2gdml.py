import pyg4ometry as _pyg4
import numpy as _np

def stl2gdml(stlFileName, gdmlFileName = "output.gdml", worldMaterial = "G4_Galactic", solidMaterial="G4_Au") :
    r = _pyg4.stl.Reader(stlFileName, centre=True)
    reg = r.getRegistry()
    s = r.getSolid()

    if type(worldMaterial) == str :
        wm = _pyg4.geant4.MaterialPredefined(worldMaterial)
    else :
        wm = worldMaterial

    if type(solidMaterial) == str :
        sm = _pyg4.geant4.MaterialPredefined(solidMaterial)
    else :
        sm = solidMaterial

    sl = _pyg4.geant4.LogicalVolume(s, sm, "bl", reg)

    e  = _np.array(sl.extent(True))
    de = e[1] - e[0]
    de = 1.1*de

    ws = _pyg4.geant4.solid.Box("ws",de[0],de[1],de[2], reg)
    wl = _pyg4.geant4.LogicalVolume(ws, wm, "wl", reg)

    sp = _pyg4.geant4.PhysicalVolume([0,0,0],[0,0,0],  sl, "s_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    w = _pyg4.gdml.Writer()
    w.addDetector(reg)
    w.write(gdmlFileName)

