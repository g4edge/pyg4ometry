import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.misc as _mi


def Test_MaterialsRegistry(outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "500", reg, True)
    wy = _gd.Constant("wy", "500", reg, True)
    wz = _gd.Constant("wz", "500", reg, True)

    #######################################################################################
    wm = _g4.MaterialPredefined("G4_Galactic", reg)

    bm1 = _g4.MaterialPredefined("G4_Fe", reg)
    bm2 = _g4.MaterialSingleElement("iron", 26, 55.8452, 7.874, reg)  # iron at near room temp

    bm3 = _g4.MaterialCompound("air", 1.290e-3, 2, reg)
    ne = _g4.ElementSimple("nitrogen", "N", 7, 14.01, reg)
    oe = _g4.ElementSimple("oxygen", "O", 8, 16.0, reg)
    bm3.add_element_massfraction(ne, 0.7)
    bm3.add_element_massfraction(oe, 0.3)

    bm3 = _g4.MaterialCompound("water", 1.0, 2, reg)
    he = _g4.ElementSimple("hydrogen", "H", 1, 1.01, reg)
    bm3.add_element_natoms(he, 2)
    bm3.add_element_natoms(oe, 1)

    copper = _g4.MaterialPredefined("G4_Cu", reg)
    zinc = _g4.MaterialPredefined("G4_Zn", reg)
    bm4 = _g4.MaterialCompound("YellowBrass_C26800", 8.14, 2, reg)
    bm4.add_material(copper, 0.67)
    bm4.add_material(zinc, 0.33)

    u235 = _g4.Isotope("U235", 92, 235, 235.044, reg)  # Explicitly registered
    u238 = _g4.Isotope("U238", 92, 238, 238.051)  # Not explicitly registered
    uranium = _g4.ElementIsotopeMixture("uranium", "U", 2, reg)
    uranium.add_isotope(u235, 0.00716)
    uranium.add_isotope(u238, 0.99284)
    bm5 = _g4.MaterialCompound("natural_uranium", 19.1, 2, reg)
    bm5.add_element_massfraction(uranium, 1)

    bm6 = _g4.MaterialCompound("RadioactiveBrass", 8.14, 2, reg)
    bm6.add_material(bm4, 0.99)
    bm6.add_material(bm5, 0.01)

    #######################################################################################

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")

    bs = _g4.solid.Box("bs", 10, 10, 10, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)

    bl1 = _g4.LogicalVolume(bs, bm1, "bl1", reg)
    bl2 = _g4.LogicalVolume(bs, bm2, "bl2", reg)
    bl3 = _g4.LogicalVolume(bs, bm3, "bl3", reg)
    bl4 = _g4.LogicalVolume(bs, bm4, "bl4", reg)  # Material specified by object
    bl5 = _g4.LogicalVolume(bs, "natural_uranium", "bl5", reg)  # Material specified by name
    bl6 = _g4.LogicalVolume(bs, "RadioactiveBrass", "bl6", reg)

    bp1 = _g4.PhysicalVolume([0, 0, 0], [40, 0, 0], bl1, "b_pv1", wl, reg)
    bp2 = _g4.PhysicalVolume([0, 0, 0], [0, 40, 0], bl2, "b_pv2", wl, reg)
    bp3 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 40], bl3, "b_pv3", wl, reg)
    bp4 = _g4.PhysicalVolume([0, 0, 0], [20, 20, 20], bl4, "b_pv4", wl, reg)
    bp5 = _g4.PhysicalVolume([0, 0, 0], [-20, -20, -20], bl5, "b_pv5", wl, reg)
    bp6 = _g4.PhysicalVolume([0, 0, 0], [-40, 0, 0], bl6, "b_pv6", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # Order the materials - not generally needed for a normal workflow
    reg.orderMaterials()
    assert len(reg.materialList) > 0  # Ensure the material list is populated

    # gdml output
    outputFile = outputPath / "T203_MaterialsRegistry.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)
