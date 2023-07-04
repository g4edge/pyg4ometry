import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry, Material, Compound


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    fr = Material("FRANCIUM", 87, 2.48, flukaregistry=freg)
    es = Material("EINSTEIN", 99, 8.84, flukaregistry=freg)

    fr2es3 = Compound(
        "Fr2Es3", 7.5, [(fr, 2.0), (es, 3.0)], fractionType="mass", flukaregistry=freg
    )

    card = fr2es3.toCards()

    rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    zone = Zone()
    zone.addIntersection(rpp)
    region = Region("RPP_REG")  # should this be string or

    # material instance or maybe either?
    region.addZone(zone)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    freg.addMaterialAssignments(fr2es3, region)

    greg = convert.fluka2Geant4(freg)

    lvmat = greg.logicalVolumeDict["RPP_REG_lv"].material
    comp = lvmat.components
    first = comp[0]
    second = comp[1]

    assert first[0].name == "FRANCIUM"
    assert first[1] == 0.4
    assert first[2] == "massfraction"

    assert second[0].name == "EINSTEIN"
    assert second[1] == 0.6
    assert second[2] == "massfraction"

    greg.getWorldVolume().clipSolid()

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}


if __name__ == "__main__":
    Test(True, True)
