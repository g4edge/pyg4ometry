from pyg4ometry import convert, fluka


def _addRegion(freg, name, *bodies):
    zone = fluka.Zone()
    for body in bodies:
        zone.addIntersection(body)
    region = fluka.Region(name)
    region.addZone(zone)
    freg.addRegion(region)
    return region


def test_body_only_in_null_region_with_several_regions():
    # Two real regions plus a null region (intersection of disjoint boxes) with its own
    # bodies. The null region is dropped when minimising solids, so its bodies are used by
    # no converted region and have no aabb. This used to crash on reduce of an empty list.
    freg = fluka.FlukaRegistry()
    box1 = fluka.RPP("BOX1", -10, 0, -10, 10, -10, 10, flukaregistry=freg)
    box2 = fluka.RPP("BOX2", 0, 10, -10, 10, -10, 10, flukaregistry=freg)
    nullA = fluka.RPP("NULLA", 20, 30, -10, 10, -10, 10, flukaregistry=freg)
    nullB = fluka.RPP("NULLB", 40, 50, -10, 10, -10, 10, flukaregistry=freg)

    reg1 = _addRegion(freg, "REG1", box1)
    reg2 = _addRegion(freg, "REG2", box2)
    regNull = _addRegion(freg, "NULLREG", nullA, nullB)
    freg.assignma("COPPER", reg1, reg2, regNull)

    greg = convert.fluka2Geant4(freg, minimiseSolids=True)

    daughters = {pv.logicalVolume.name for pv in greg.getWorldVolume().daughterVolumes}
    assert daughters == {"REG1_lv", "REG2_lv"}
