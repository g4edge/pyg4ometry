import os as _os

import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml   as _gd

def Test_MaterialPredefined() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic")
    bm = _g4.MaterialPredefined("G4_Fe")
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialPredefined.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialPredefined.gmad"),"T201_MaterialPredefined.gdml")

def Test_MaterialSingleElement() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialSingleElement("galactic",1,1.008,1e-25,reg)   # low density hydrogen
    bm = _g4.MaterialSingleElement("iron",26,55.8452,7.874,reg)    # iron at near room temp
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialSingleElement.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialSingleElement.gmad"),"T201_MaterialSingleElement.gdml")

def Test_MaterialCompoundMassFraction() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialCompound("air",1.290e-3,2,reg)
    ne = _g4.ElementSimple("nitrogen","N",7,14.01)
    oe = _g4.ElementSimple("oxygen","O",8,16.0)
    wm.add_element_massfraction(ne,0.7)
    wm.add_element_massfraction(oe,0.3)
    bm = _g4.MaterialSingleElement("iron",26,55.8452,7.874,reg)    # iron at near room temp
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialCompoundMassFraction.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialCompoundMassFraction.gmad"),"T201_MaterialCompoundMassFractiion.gdml")


def Test_MaterialCompoundAtoms() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic")
    #bm = _g4.MaterialCompound("plastic",1.38,3,reg)    # Generic PET C_10 H_8 O_4
    #he = _g4.ElementSimple("hydrogen","H",1,1.008)
    #ce = _g4.ElementSimple("carbon","C",6,12.0096)
    #oe = _g4.ElementSimple("oxygen","O",8,16.0)
    #bm.add_element_natoms(he,8)
    #bm.add_element_natoms(ce,10)
    #bm.add_element_natoms(oe,4)

    bm = _g4.MaterialCompound("water", 1.0, 2, reg)
    he = _g4.ElementSimple("hydrogen", "H", 1, 1.01)
    oe = _g4.ElementSimple("oxygen", "O", 8, 16.0)
    bm.add_element_natoms(he, 2)
    bm.add_element_natoms(oe, 1)
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)

    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialCompoundNumberAtoms.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialCompoundNumberAtoms.gmad"),"T201_MaterialCompoundNumberAtoms.gdml")

def Test_MaterialMixture():

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic")
    copper = _g4.MaterialPredefined("G4_Cu")
    zinc   = _g4.MaterialPredefined("G4_Zn")
    bm     = _g4.MaterialCompound("YellowBrass_C26800", 8.14, 2, reg)
    bm.add_material(copper, 0.67)
    bm.add_material(zinc, 0.33)
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)

    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialMixture.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialMixture.gmad"),"T201_MaterialMixture.gdml")


def Test_MaterialIsotopes():

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic")

    u235 = _g4.Isotope("U235", 92, 235, 235.044)
    u238 = _g4.Isotope("U238", 92, 238, 238.051)
    uranium = _g4.ElementIsotopeMixture("uranium", "U", 2)
    uranium.add_isotope(u235, 0.00716)
    uranium.add_isotope(u238, 0.99284)

    bm = _g4.MaterialCompound("natural_uranium", 19.1, 2, reg)
    bm.add_element_massfraction(uranium, 1)
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialIsotopes.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialIsotopes.gmad"),"T201_MaterialIsotopes.gdml")



def Test_MaterialPressureTemperature() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialCompound("air",1.290e-3,2,reg)
    ne = _g4.ElementSimple("nitrogen","N",7,14.01)
    oe = _g4.ElementSimple("oxygen","O",8,16.0)
    wm.add_element_massfraction(ne,0.7)
    wm.add_element_massfraction(oe,0.3)
    wm.set_pressure(1100, "pascal")
    wm.set_temperature(293.15)

    # Enure the state variables are set properly
    assert wm.state_variables["temperature"] == 293.15
    assert wm.state_variables["temperature_unit"] == "K"  # Check the default unit
    assert wm.state_variables["pressure"] == 1100
    assert wm.state_variables["pressure_unit"] == "pascal"

    bm = _g4.MaterialSingleElement("iron",26,55.8452,7.874,reg)    # iron at near room temp
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialPressureTemperature.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialPressureTemperature.gmad"),"T201_MaterialPressureTemperature.gdml")


def Test_MaterialState() :

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    bx = _gd.Constant("bx", "10", reg, True)
    by = _gd.Constant("by", "10", reg, True)
    bz = _gd.Constant("bz", "10", reg, True)

    #######################################################################################
    wm = _g4.MaterialCompound("air",1.290e-3,2,reg)
    ne = _g4.ElementSimple("nitrogen","N",7,14.01)
    oe = _g4.ElementSimple("oxygen","O",8,16.0)
    wm.add_element_massfraction(ne,0.7)
    wm.add_element_massfraction(oe,0.3)
    wm.set_state("liquid")

    # Enure the state is set properly
    assert wm.state == "liquid"

    bm = _g4.MaterialSingleElement("iron",26,55.8452,7.874,reg)    # iron at near room temp
    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    bs = _g4.solid.Box("bs", bx, by, bz, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    bl = _g4.LogicalVolume(bs, bm, "bl", reg)
    bp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], bl, "b_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T201_MaterialState.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),"T201_MaterialState.gmad"),"T201_MaterialState.gdml")