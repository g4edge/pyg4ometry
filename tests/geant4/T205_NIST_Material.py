import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.misc as _mi


def Test_NIST_Material(outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "500", reg, True)
    wy = _gd.Constant("wy", "500", reg, True)
    wz = _gd.Constant("wz", "500", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic", reg)

    #######################################################################################
    bm1 = _g4.nist_material_2geant4Material("G4_CONCRETE", reg)
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
    outputFile = outputPath / "T205_NIST_Element.gdml"
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputFile)

    # check file
    _mi.compareGdmlNumericallyWithAssert(refFilePath, outputFile)


if __name__ == "__main__":
    Test_NIST_Material()
