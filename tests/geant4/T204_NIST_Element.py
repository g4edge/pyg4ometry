import os as _os

import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml   as _gd

def Test_NIST_Element():
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "500", reg, True)
    wy = _gd.Constant("wy", "500", reg, True)
    wz = _gd.Constant("wz", "500", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic", reg)

    #######################################################################################
    bm1 = _g4.nist_material_2geant4Material('G4_H', reg)
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")

    bs = _g4.solid.Box("bs", 10, 10, 10, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl1 = _g4.LogicalVolume(bs, bm1, "bl1", reg)
    bp1 = _g4.PhysicalVolume([0, 0, 0], [40, 0, 0], bl1, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # Order the materials - not generally needed for a normal workflow
    reg.orderMaterials()
    assert len(reg.materialList) > 0  # Ensure the material list is populated

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    name = "T204_NIST_Element"
    w.write(_os.path.join(_os.path.dirname(__file__), name+".gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),name+".gmad"),name+".gdml")
