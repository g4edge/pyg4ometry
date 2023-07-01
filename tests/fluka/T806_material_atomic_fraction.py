import os
import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry import gdml
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry, Material, Compound


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    fr = Material("FRANCIUM", 50, 2, flukaregistry=freg)
    es = Material("EINSTEIN", 100, 8, flukaregistry=freg)

    frFrac = 0.5
    frEs = 0.5

    fr2es3 = Compound(
        "Fr2Es3",
        7.5,
        [(fr, frFrac), (es, frEs)],
        fractionType="atomic",
        flukaregistry=freg,
    )

    card = fr2es3.toCards()

    rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    zone = Zone()
    zone.addIntersection(rpp)
    region = Region("RPP_REG")  # should this be string or

    # material instance or maybe either?
    region.addZone(zone)
    freg.addRegion(region)

    freg.addMaterialAssignments(fr2es3, region)

    greg = convert.fluka2Geant4(freg)

    lvmat = greg.logicalVolumeDict["RPP_REG_lv"].material
    comp = lvmat.components
    first = comp[0]
    second = comp[1]

    assert first[0].name == "FRANCIUM"
    assert first[2] == "massfraction"

    assert second[0].name == "EINSTEIN"
    assert second[2] == "massfraction"

    greg.getWorldVolume().clipSolid()

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    w = gdml.Writer()
    w.addDetector(greg)
    gdml_name = "atom.inp".rstrip(".inp") + ".gdml"
    gmad_name = "atom.inp".rstrip(".inp") + ".gmad"
    w.write(os.path.join(os.path.dirname(__file__), gdml_name))
    w.writeGmadTester(gmad_name, gdml_name)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}


if __name__ == "__main__":
    Test(True, True)
