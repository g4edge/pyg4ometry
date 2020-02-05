import logging
from copy import deepcopy
import warnings
import types

import numpy as np

import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans
from pyg4ometry.fluka.vector import (Extent,
                                     areExtentsOverlapping,
                                     applyTransform,
                                     applyTransformRotation)
from pyg4ometry.fluka.region import areOverlapping


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WORLD_DIMENSIONS = [10000, 10000, 10000]

def fluka2Geant4(flukareg,
                 regions=None,
                 withLengthSafety=True,
                 splitDisjointUnions=True,
                 minimiseSolids=True,
                 worldMaterial="G4_Galactic",
                 worldDimensions=None,
                 omitBlackholeRegions=True,
                 materialMap=None,
                 omitRegions=None,
                 quadricRegionExtents=None):

    _checkQuadric(flukareg, quadricRegionExtents)

    regions = _getSelectedRegions(flukareg, regions, omitRegions)

    if omitBlackholeRegions:
        flukareg = _without_blackhole_regions(flukareg, regions)

    if withLengthSafety:
        flukareg = _make_length_safety_registry(flukareg, regions)

    if splitDisjointUnions:
        flukareg, newNamesToOldNames = _make_disjoint_unions_registry(flukareg,
                                                                      regions)

        newRegions = []
        for newName, oldName in newNamesToOldNames.iteritems():
            if oldName in regions:
                newRegions.append(newName)
        regions = newRegions

    worldDimensions = _getWorldDimensions(worldDimensions)
    materialMap = _getMaterialMap(materialMap)

    greg = g4.Registry()

    wlv = _makeWorldVolume(worldDimensions, worldMaterial, greg)

    extentMap = None
    if minimiseSolids:
        region_extents = _get_region_extents(flukareg, regions)
        extentMap = _make_body_minimum_extentMap(flukareg,
                                                 region_extents,
                                                 regions)
        flukareg = _filterHalfSpaces(flukareg, region_extents)
    elif flukareg.latticeDict:
        # Don't pass a subset of the region name here because for
        # LATTICE we need to consider all regions.  E.g. if we want to
        # copy the cell but not the prototype.
        region_extents = _get_region_extents(flukareg, flukareg.regionDict)

    regionsWithLVs = {}
    # Do non-lattice regions first as we convert the lattices in the
    # loop after this, as they must be treated differently.
    nonLatticeRegions = flukareg.getNonLatticeRegions()
    for name, region in nonLatticeRegions.iteritems():
        if name not in regions:
            continue

        region = flukareg.regionDict[name]
        region_solid = region.geant4Solid(greg, extent=extentMap)

        region_material = region.material
        if region_material is None:
            warnings.warn(
                "Setting None material in region {} to G4_Fe.".format(
                    name))
            region_material = g4.MaterialPredefined("G4_Fe")

        elif region_material in materialMap:
            region_material = materialMap[region_material]
        else:
            # warnings.warn("Region {} material being set to G4_Fe.".format(name))
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
                          list(region.centre(extent=extentMap)),
                          region_lv,
                          "{}_pv".format(name),
                          wlv, greg)

    # If not lattices defined then we end the conversion here.
    if not flukareg.latticeDict:
        greg.setWorld(wlv.name)
        return greg
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
    worldMaterial = g4.MaterialPredefined(material)

    world_solid = g4.solid.Box("world_solid",
                               dimensions[0],
                               dimensions[1],
                               dimensions[2], g4registry, "mm")
    wlv = g4.LogicalVolume(world_solid, worldMaterial, "wl", g4registry)
    return wlv

def _make_length_safety_registry(flukareg, regions):
    bigger = fluka.FlukaRegistry()
    smaller = fluka.FlukaRegistry()

    for body in flukareg.bodyDict.itervalues():
        bigger.addBody(body.safetyExpanded())
        smaller.addBody(body.safetyShrunk())

    # return bigger, smaller
    fluka_reg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if name not in regions:
            continue

        ls_region = region.withLengthSafety(bigger, smaller)
        fluka_reg_out.addRegion(ls_region)
        ls_region.allBodiesToRegistry(fluka_reg_out)
    fluka_reg_out.latticeDict = flukareg.latticeDict
    return fluka_reg_out

def _make_disjoint_unions_registry(flukareg, regions):
    fluka_reg_out = fluka.FlukaRegistry()
    newNamesToOldNames = {}
    for name, region in flukareg.regionDict.iteritems():
        if name not in regions:
            continue
        if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            newNamesToOldNames[name] = name
            continue

        connected_zones = region.get_connected_zones()
        if len(connected_zones) == 1: # then there are no disjoint unions
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            newNamesToOldNames[name] = name
            continue

        for connection in connected_zones: # loop over the connections
            # make new region with appropriate name
            zones_string = "_".join(map(str, connection))
            new_region_name = "{}_djz{}".format(name, zones_string)
            new_region = fluka.Region(new_region_name, material=region.material)
            newNamesToOldNames[new_region_name] = name
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
    return fluka_reg_out, newNamesToOldNames

def _get_region_extents(flukareg, regions):
    regionmap = flukareg.regionDict
    regionExtents = {}
    for name, region in regionmap.iteritems():
        if name not in regions:
            continue
        regionExtents[name] = region.extent()
    return regionExtents

def _make_body_minimum_extentMap(flukareg, region_extents, regions):
    bodies_to_regions = flukareg.getBodyToRegionsMap()

    bodies_to_minimum_extents = {}
    for body_name, region_names in bodies_to_regions.iteritems():
        logger.debug("Getting minimum extent for body: %s", body_name)

        bodyRegionExtents = []
        for region_name in region_names:
            if region_name not in regions:
                continue
            bodyRegionExtents.append(region_extents[region_name])

        if len(region_extents) == 1:
            extent = region_extents.values()[0]
        elif len(region_extents) > 1:
            extent = reduce(_getMaximalOfTwoExtents, bodyRegionExtents)
            logger.debug("Minimum extent = %s", extent)
        else:
            raise ValueError("WHAT?")

        bodies_to_minimum_extents[body_name] = extent

    return bodies_to_minimum_extents

def _getMaximalOfTwoExtents(extent1, extent2):
    # Get combined extents which are greatest
    lower = [min(a, b) for a, b in zip(extent1.lower, extent2.lower)]
    upper = [max(a, b) for a, b in zip(extent1.upper, extent2.upper)]
    return fluka.Extent(lower, upper)

def _without_blackhole_regions(flukareg, regions):
    freg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if region.material == "BLCKHOLE":
            continue
        if name not in regions:
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

def _checkQuadric(flukareg, quadricRegionExtents):
    for region_name, region in flukareg.regionDict.iteritems():
        regionBodies = region.bodies()
        quadrics = {r for r in regionBodies if isinstance(r, fluka.QUA)}

        if not quadrics:
            continue

        if quadricRegionExtents is None:
            msg = "quadricRegionExtents must be set for regions with QUAs."
            raise ValueError(msg)

        for q in quadrics:
            if q.name not in quadricRegionExtents:
                msg = ("Region {} with QUA missing "
                       "extent in quadricRegionExtents.".format(region_name))
                raise ValueError(msg)


def _getWorldDimensions(worldDimensions):
    if worldDimensions is None:
        return WORLD_DIMENSIONS
    return worldDimensions

def _getMaterialMap(materialMap):
    if not materialMap:
        return {}
    return materialMap

def _getSelectedRegions(flukareg, regions, omitRegions):
    if not flukareg.regionDict:
        raise ValueError("No regions in registry.")
    elif regions and omitRegions:
        raise ValueError("Only one of regions and omitRegions may be set.")
    elif omitRegions:
        return set(flukareg.regionDict).difference(omitRegions)
    elif regions is None:
        return list(flukareg.regionDict)

def _filterHalfSpaces(flukareg, extents):
    fout = fluka.FlukaRegistry()
    logger.debug("Filtering half spaces")

    for region_name, region in flukareg.regionDict.iteritems():
        regionOut = deepcopy(region)
        regionExtent = extents[region_name]
        for body in regionOut.bodies():
            if isinstance(body, (fluka.XYP, fluka.XZP,
                                 fluka.YZP, fluka.PLA)):
                normal, pointOnPlane = body.toPlane()
                extentCornerDistance = regionExtent.cornerDistance()
                d = _distanceFromPointToPlane(normal, pointOnPlane,
                                              regionExtent.centre)
                if d > 1.1 * extentCornerDistance:
                    logger.debug(
                        ("Filtering %s from region %s."
                         "  extent = %s, extentMax = %s, d=%s"),
                        body, region_name, regionExtent,
                        extentCornerDistance, d)
                    regionOut.removeBody(body.name)
        fout.addRegion(regionOut)
        regionOut.allBodiesToRegistry(fout)
    return fout

def _distanceFromPointToPlane(normal, pointOnPlane, point):
    normal = fluka.Three(normal).unit()
    return abs(np.dot(normal, point - pointOnPlane))
