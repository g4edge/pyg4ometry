from copy import deepcopy
import warnings

import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans

WORLD_DIMENSIONS = 10000

def fluka2Geant4(flukareg, with_length_safety=True,
                 split_disjoint_unions=True):
    if with_length_safety:
        flukareg = _make_length_safety_registry(flukareg)

    if split_disjoint_unions:
        flukareg = _make_disjoint_unions_registry(flukareg)

    if not flukareg.regionDict:
        raise ValueError("No regions in registry.")

    greg = g4.Registry()

    world_material = g4.MaterialPredefined("G4_Galactic")

    world_solid = g4.solid.Box("world_solid",
                               WORLD_DIMENSIONS,
                               WORLD_DIMENSIONS,
                               WORLD_DIMENSIONS, greg, "mm")
    wlv = g4.LogicalVolume(world_solid, world_material, "wl", greg)



    for name, region in flukareg.regionDict.iteritems():
        region_solid = region.geant4_solid(greg)
        region_material = g4.MaterialPredefined("G4_Fe")
        region_lv = g4.LogicalVolume(region_solid,
                                     region_material,
                                     "{}_lv".format(name),
                                     greg)
        # We reverse because rotations in the context of Booleans are
        # active, and that is the convention we have followed so far,
        # but volume rotations are passive, so we have to reverse the
        # rotation.
        rot = list(trans.reverse(region.tbxyz()))
        g4.PhysicalVolume(rot,
                          list(region.centre()),
                          region_lv,
                          "{}_pv".format(name),
                          wlv, greg)

    greg.setWorld(wlv.name)
    return greg

def _make_length_safety_registry(flukareg):
    bigger = fluka.FlukaRegistry()
    smaller = fluka.FlukaRegistry()

    for body in flukareg.bodyDict.itervalues():
        try:
            bigger.addBody(body.safety_expanded())
            smaller.addBody(body.safety_shrunk())
        except AttributeError:
            warnings.warn(
                "No length safety supported for body type {}.".format(
                    type(body).__name__))
            bigger.addBody(body)
            smaller.addBody(body)

    # return bigger, smaller
    fluka_reg_out = fluka.FlukaRegistry()
    for region in flukareg.regionDict.itervalues():
        ls_region = region.with_length_safety(bigger, smaller)
        fluka_reg_out.addRegion(ls_region)
        ls_region.allBodiesToRegistry(fluka_reg_out)

    return fluka_reg_out

def _make_disjoint_unions_registry(flukareg):
    fluka_reg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
            fluka_reg_out.addRegion(deepcopy(region))
            continue

        connected_zones = region.get_connected_zones()
        if len(connected_zones) == 1: # then there are no disjoint unions
            fluka_reg_out.addRegion(deepcopy(region))
            continue

        for connection in connected_zones: # loop over the connections

            # make new region with appropriate name
            zones_string = "_".join(map(str, connection))
            new_region_name = "{}_djz{}".format(name, zones_string)
            new_region = fluka.Region(new_region_name, material=region.material)

            # get the zones which are connected
            zones = [(i, region.zones[i]) for i in connection]
            for index, zone in zones:
                # copy teh zone, give it a new name since it now
                # belongs to a different region.
                new_zone = deepcopy(zone)
                new_zone.name = "{}_djz_z{}".format(new_zone.name, index)
                new_region.addZone(new_zone)
                new_region.allBodiesToRegistry(fluka_reg_out)
                fluka_reg_out.addRegion(new_region)

    return fluka_reg_out
