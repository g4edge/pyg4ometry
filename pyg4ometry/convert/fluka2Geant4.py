import logging
from copy import deepcopy
import warnings
import types

import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans
from pyg4ometry.fluka.vector import (Extent,
                                     areExtentsOverlapping,
                                     applyTransform,
                                     applyTransformRotation)
from pyg4ometry.fluka.region import areOverlapping


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

WORLD_DIMENSIONS = 10000

def fluka2Geant4(flukareg, with_length_safety=True,
                 split_disjoint_unions=True,
                 minimise_solids=True,
                 world_material="G4_Galactic",
                 omit_blackhole_regions=True):

    if omit_blackhole_regions:
        flukareg = _without_blackhole_regions(flukareg)

    if with_length_safety:
        flukareg = _make_length_safety_registry(flukareg)

    if split_disjoint_unions:
        flukareg = _make_disjoint_unions_registry(flukareg)

    if not flukareg.regionDict:
        raise ValueError("No regions in registry.")

    greg = g4.Registry()

    wlv = _makeWorldVolume(WORLD_DIMENSIONS, world_material, greg)

    extent_map = None
    if minimise_solids:
        region_extents = _get_region_extents(flukareg)
        extent_map = _make_body_minimum_extent_map(flukareg, region_extents)
    elif flukaregistry.latticeDict:
        region_extents = _get_region_extents(flukareg)

    regionsWithLVs = {}
    # Do non-lattice regions first as we convert the lattices in the
    # loop after this, as they must be treated differently.
    nonLatticeRegions = flukareg.getNonLatticeRegions()
    for name, region in nonLatticeRegions.iteritems():
        region = flukareg.regionDict[name]
        region_solid = region.geant4Solid(greg, extent=extent_map)

        region_material = region.material
        if region_material is None:
            warnings.warn("No material assigned for region {}".format(name))


        region_material = g4.MaterialPredefined("G4_Fe")
        region_lv = g4.LogicalVolume(region_solid,
                                     region_material,
                                     "{}_lv".format(name),
                                     greg)

        regionsWithLVs[name] = region_lv
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

    latticeContents = _getContentsOfLatticeCells(flukareg, region_extents)
    for latticeName, contents in latticeContents.iteritems():
        # We take the LVs associated with this lattice (which have been
        # placed above as PV) and place it with the translation and
        # rotation of the lattice cell.
        latticeRegion = flukareg.regionDict[latticeName]
        latticeCentre = list(latticeRegion.centre())
        latticeRotation = list(trans.reverse(latticeRegion.tbxyz()))

        for prototypeName in contents:
            prototypeLV = regionsWithLVs[prototypeName]
            g4.PhysicalVolume(latticeRotation,
                              latticeCentre,
                              prototypeLV,
                              "{}_lattice_pv".format(latticeName),
                              wlv, greg)

    greg.setWorld(wlv.name)
    return greg

def _makeWorldVolume(dimensions, material, g4registry):
    world_material = g4.MaterialPredefined(material)

    world_solid = g4.solid.Box("world_solid",
                               WORLD_DIMENSIONS,
                               WORLD_DIMENSIONS,
                               WORLD_DIMENSIONS, g4registry, "mm")
    wlv = g4.LogicalVolume(world_solid, world_material, "wl", g4registry)
    return wlv

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
    fluka_reg_out.latticeDict = flukareg.latticeDict
    return fluka_reg_out

def _make_disjoint_unions_registry(flukareg):
    fluka_reg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            continue

        connected_zones = region.get_connected_zones()
        if len(connected_zones) == 1: # then there are no disjoint unions
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
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
    fluka_reg_out.latticeDict = flukareg.latticeDict
    return fluka_reg_out

def _get_region_extents(flukareg):
    regionmap = flukareg.regionDict
    return {name: region.extent() for name, region in regionmap.iteritems()}

def _make_body_minimum_extent_map(flukareg, region_extents):
    bodies_to_regions = flukareg.getBodyToRegionsMap()

    bodies_to_minimum_extents = {}
    for body_name, region_names in bodies_to_regions.iteritems():
        _logger.debug("Getting minimum extent for body: %s", body_name)
        body_region_extents = [region_extents[region_name]
                               for region_name in region_names]
        if len(region_extents) == 1:
            extent = region_extents.values()[0]
        elif len(region_extents) > 1:
            extent = reduce(_getMaximalOfTwoExtents, body_region_extents)
            _logger.debug("Minimum extent = %s", extent)
        else:
            raise ValueError("WHAT?")

        bodies_to_minimum_extents[body_name] = extent

    return bodies_to_minimum_extents

def _getMaximalOfTwoExtents(extent1, extent2):
    # Get combined extents which are greatest
    lower = [min(a, b) for a, b in zip(extent1.lower, extent2.lower)]
    upper = [max(a, b) for a, b in zip(extent1.upper, extent2.upper)]
    return fluka.Extent(lower, upper)

def _without_blackhole_regions(flukareg):
    freg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if region.material == "BLCKHOLE":
            continue
        freg_out.addRegion(region)
        region.allBodiesToRegistry(freg_out)
    freg_out.latticeDict = flukareg.latticeDict
    return freg_out

def _getOverlappingExtents(extent, extents):
    overlappingExtents = []
    for name, e in extents.iteritems():
        if areExtentsOverlapping(extent, e):
            overlappingExtents.append(name)
    return overlappingExtents

def _getContentsOfLatticeCells(flukaregistry, regionExtents):
    lattice = flukaregistry.latticeDict
    regions = flukaregistry.regionDict

    cellContents = {}
    for cellName, transform in lattice.iteritems():
        cellRegion = regions[cellName]

        transformedCellExtent = _getTransformedCellRegionExtent(cellRegion,
                                                                transform)
        overlappingExents = _getOverlappingExtents(transformedCellExtent,
                                                   regionExtents)
        cellContents[cellName] = []
        for regionName in overlappingExents:
            region = regions[regionName]
            overlapping = _isTransformedCellRegionIntersectingWithRegion(
                region, cellRegion, transform)
            if overlapping:
                cellContents[cellName].append(regionName)

    return cellContents

def _getTransformedCellRegionExtent(cellRegion, latticeTransform):
    # Move the lattice cell region onto the prototype region.
    cellRotation = applyTransformRotation(latticeTransform,
                                          cellRegion.rotation())
    cellCentre = list(applyTransform(latticeTransform, cellRegion.centre()))
    cellName = cellRegion.name
    greg = g4.Registry()
    wlv = _makeWorldVolume(WORLD_DIMENSIONS, "G4_Galactic", greg)


    region_solid = cellRegion.geant4Solid(greg, extent=None)
    region_lv = g4.LogicalVolume(region_solid,
                                 "G4_Galactic",
                                 "{}_lv".format(cellName),
                                 greg)

    # Invert the rotation as usual and convert to tbxyz
    cellRotation = list(trans.matrix2tbxyz(cellRotation.T))
    g4.PhysicalVolume(cellRotation,
                      cellCentre,
                      region_lv,
                      "{}_pv".format(cellName),
                      wlv, greg)

    lower, upper = wlv.extent()
    extent = fluka.Extent(lower, upper)

    return extent

def _isTransformedCellRegionIntersectingWithRegion(region,
                                                   cellRegion,
                                                   latticeTransform):
    cellRegion = deepcopy(cellRegion)
    cellRotation = applyTransformRotation(latticeTransform,
                                          cellRegion.rotation())
    cellCentre = applyTransform(latticeTransform,
                                cellRegion.centre())

    # XXX: Nasty hack to get the cellRegion to return the rotation and
    # centre that I want it to return.  These two lines save me a lot
    # of work elsewhere.
    def rotation(self): return cellRotation
    def centre(self, extent=None): return cellCentre
    cellRegion.rotation = types.MethodType(rotation, cellRegion)
    cellRegion.centre = types.MethodType(centre, cellRegion)

    return areOverlapping(cellRegion, region)
