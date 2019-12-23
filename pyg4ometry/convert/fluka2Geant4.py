import logging
from copy import deepcopy
import warnings

import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

WORLD_DIMENSIONS = 10000

def fluka2Geant4(flukareg, with_length_safety=True,
                 split_disjoint_unions=True,
                 minimise_solids=True):

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

    extent_map = {body: None for body in flukareg.bodyDict}
    if minimise_solids:
        extent_map = _make_body_minimum_extent_map(flukareg)

    for name, region in flukareg.regionDict.iteritems():
        region_solid = region.geant4Solid(greg, extent_map)
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
                          list(region.centre(extent=extent_map)),
                          region_lv,
                          "{}_pv".format(name),
                          wlv, greg)

    greg.setWorld(wlv.name)
    return greg

def _make_length_safety_registry(flukareg):
    bigger = fluka.FlukaRegistry()
    smaller = fluka.FlukaRegistry()

    for body in flukareg.bodyDict.itervalues():
        bigger.addBody(body.safetyExpanded())
        smaller.addBody(body.safetyShrunk())

    # return bigger, smaller
    fluka_reg_out = fluka.FlukaRegistry()
    for region in flukareg.regionDict.itervalues():
        ls_region = region.withLengthSafety(bigger, smaller)
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

def _get_region_extents(flukareg):
    regionmap = flukareg.regionDict
    return {name: region.extent() for name, region in regionmap.iteritems()}

def _make_body_minimum_extent_map(flukareg):
    region_extents = _get_region_extents(flukareg)
    bodies_to_regions = flukareg.getBodyToRegionsMap()

    bodies_to_minimum_extents = {}
    for body_name, region_names in bodies_to_regions.iteritems():
        _logger.debug("Getting minimum extent for body: %s", body_name)
        body_region_extents = [region_extents[region_name]
                               for region_name in region_names]
        if len(region_extents) == 1:
            extent = region_extents[0]
        elif len(region_extents) > 1:
            # _logger.debug("Reducing to minimum extent: %s",
            #               body_region_extents)
            extent = reduce(_getMaximalOfTwoExtents, body_region_extents)
            _logger.debug("Minimum extent = %s", extent)
        else:
            raise ValueError("WHAT?")

        bodies_to_minimum_extents[body_name] = extent

    return bodies_to_minimum_extents

def _getMaximalOfTwoExtents(extent1, extent2):
    # Get combined extents which are greatest
    lower = [min(a, b) for a, b in zip(extent1.lower, extent2.lower)]
    upper = [max(a, b) for a, b in zip(extent1.uppwer, extent2.upper)]
    return fluka.Extent(lower, upper)
