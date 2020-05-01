from functools import reduce
import logging
from copy import deepcopy
import logging
import types
import warnings

import numpy as np

from .fluka2g4materials import makeFlukaToG4MaterialsMap
from pyg4ometry import exceptions
from pyg4ometry.fluka import Transform
from pyg4ometry.fluka.region import areOverlapping
from pyg4ometry.fluka.vector import (Extent, areExtentsOverlapping)
import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans

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
                 omitRegions=None,
                 quadricRegionExtents=None):
    """Convert a FLUKA registry to a Geant4 Registry.

    :param flukareg: FlukaRegistry instance to be converted.
    :type flukareg: FlukaRegistry
    :param regions: Names of regions to be converted, by default \
    all are converted.  Mutually exclusive with omitRegions.
    :type regions: list
    :param withLengthSafety: Whether or not to apply automatic length safety.
    :type withLengthSafety: bool
    :param splitDisjointUnions: Whether or not to split disjoint unions into \
    separate regions before conversion.
    :type splitDisjointUnions: bool
    :param minimiseSolids: Whether or not to minimise the boxes and tubes of \
    Geant4 used to represent infinite solids in FLUKA.
    :type minimiseSolids: bool
    :param worldMaterial: name of world material to be used.
    :type worldMaterial: string
    :param worldDimensions: dimensions of world logical volume in \
    converted Geant4.  By default this is equal to WORLD_DIMENSIONS.
    :type worldDimensions: list
    :param omitBlackholeRegions: whether or not to omit regions with
    the FLUKA material BLCKHOLE from the conversion.
    :type omitBlackholeRegions: bool
    :param omitRegions: Names of regions to be omitted from the \
    conversion.  This option is mutually exclusive with the kwarg regions.
    :type omitRegions: list
    :param quadricRegionExtents: The axis-aligned extents of any regions \
    featuring QUA bodies, mapping region names to fluka.Extent instances.
    :type quadricRegionExtents: dict

    """
    fr = flukareg # abbreviation

    # Filter region names and check inputs
    regions = _getSelectedRegions(fr, regions, omitRegions)
    _checkQuadricRegionExtents(fr, quadricRegionExtents)

    if quadricRegionExtents:
        fr = _makeUniqueQuadricRegions(fr, quadricRegionExtents)
    else:
        quadricRegionExtents = {}

    if omitBlackholeRegions:
        fr = _filterBlackHoleRegions(fr, regions)

    if withLengthSafety:
        fr = _makeLengthSafetyRegistry(fr, regions)

    if splitDisjointUnions or minimiseSolids:
        regionZoneExtents = _getRegionZoneExtents(fr, regions,
                                                  quadricRegionExtents)
    if splitDisjointUnions:
        fr, newNamesToOldNames, regionZoneExtents = \
            _makeDisjointUnionsFlukaRegistry(fr, regions,
                                             regionZoneExtents,
                                             quadricRegionExtents)

        newRegions = []
        newQuadricRegionExtents = {}
        for newName, oldName in newNamesToOldNames.items():
            if oldName in regions:
                newRegions.append(newName)
            if oldName in quadricRegionExtents:
                newQuadricRegionExtents[newName] = quadricRegionExtents[oldName]

        regions = newRegions
        quadricRegionExtents = newQuadricRegionExtents

    referenceExtentMap = None
    if minimiseSolids:
        referenceExtentMap = _makeBodyMinimumReferenceExtentMap(
            fr,
            regionZoneExtents,
            regions)
        fr = _filterHalfSpaces(fr, regionZoneExtents)


    # This loop below do the main conversion
    greg = g4.Registry()
    f2g4mat = makeFlukaToG4MaterialsMap(fr, greg)

    fluka_material_names_to_g4 = makeFlukaToG4MaterialsMap(fr, greg)
    wlv = _makeWorldVolume(_getWorldDimensions(worldDimensions),
                           worldMaterial, greg)
    assignmas = fr.assignmas
    regionNamesToLVs = {}
    for name, region in fr.regionDict.items():
        if name not in regions:
            continue

        # print name
        region = fr.regionDict[name]
        region_solid = region.geant4Solid(greg,
                                          referenceExtent=referenceExtentMap)


        try:
            materialName = assignmas[name]
        except KeyError:
            raise FLUKAError("Region {} has no assigned material".format(name))

        material = f2g4mat[materialName]

        region_lv = g4.LogicalVolume(region_solid,
                                     material,
                                     "{}_lv".format(name),
                                     greg)

        regionNamesToLVs[name] = region_lv
        # We reverse because rotations in the context of Booleans are
        # active, and that is the convention we have followed so far,
        # but volume rotations are passive, so we have to reverse the
        # rotation.
        rot = list(trans.reverse(region.tbxyz()))
        g4.PhysicalVolume(
            rot,
            list(region.centre(referenceExtent=referenceExtentMap)),
            region_lv,
            "{}_pv".format(name),
            wlv, greg)

    _convertLatticeCells(greg, fr, wlv, regionZoneExtents, regionNamesToLVs)
    greg.setWorld(wlv.name)
    return greg

def _makeWorldVolume(dimensions, material, g4registry):
    """Make a world solid and logical volume with the given dimensions,
    material, and size, and add it to the geant4 Registry provided

    :param dimensions: list of 3 elements providing the dimensions in \
    [x, y, z] of the world box.
    :type dimension: list
    :param material: The name of the material to be used for the world volume.
    :type material: str
    :param g4registry: The geant4 Registry instance this world solid \
    and logical volume is to be added to.

    """
    worldMaterial = g4.MaterialPredefined(material)

    world_solid = g4.solid.Box("world_solid",
                               dimensions[0],
                               dimensions[1],
                               dimensions[2], g4registry, "mm")
    wlv = g4.LogicalVolume(world_solid, worldMaterial, "wl", g4registry)
    return wlv

def _makeLengthSafetyRegistry(flukareg, regions):
    """Make a new registry from a registry with length safety applied
    to the zones and regions within.

    :param flukareg: The FlukaRegistry from which the new registry
    with length safety applied should be built.
    :type flukareg: FlukaRegistry
    :param regions: The names of the regions that are to be converted.

    """
    # Why do I pass regions in as an argument?  Why don't I just
    # filter the FlukaRegistry instance early on and then just carry
    # on?
    bigger = fluka.FlukaRegistry()
    smaller = fluka.FlukaRegistry()

    for body in flukareg.bodyDict.values():
        bigger.addBody(body.safetyExpanded())
        smaller.addBody(body.safetyShrunk())

    # return bigger, smaller
    fluka_reg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.items():
        if name not in regions:
            continue

        ls_region = region.withLengthSafety(bigger, smaller)
        fluka_reg_out.addRegion(ls_region)
        ls_region.allBodiesToRegistry(fluka_reg_out)
    _copyStructureToNewFlukaRegistry(flukareg, fluka_reg_out)

    return fluka_reg_out

def _makeDisjointUnionsFlukaRegistry(flukareg, regions,
                                     regionZoneExtents,
                                     quadricRegionExtents):
    """Make a new FlukaRegistry in which regions with unions of
    disconnected components ("disjoint unions") are split into regions
    each consisting only of zones which are connected to each other.
    Regions that that do not feature any unions of disconnected zones
    are simply copied to the new registry.  These newly-created
    regions have names that are different to region that they
    originate from, so to preserve this information, a map of new
    region names to old region names is returned.  Additionally, a new
    map of regionZoneExtents is returned, as is necessitated by the
    fact that new regions are defined.


    :param flukareg: The FlukaRegistry instance to be transformed.
    :type flukareg: FlukaRegistry
    :param regions: The names of the regions to be converted.
    :type regions: list
    :param regionZoneExtents: A dictionary of region names to ordered \
    sequences of zone Extent instances.
    :type regionZoneExtents: dict
    :param quadricRegionExtents: Map of region names to extents \
    corresponding to the regions in which QUA bodies feature.
    :type quadricRegionExtents: dict

    """

    fluka_reg_out = fluka.FlukaRegistry()
    # Map the new region names to the name of the region that they
    # have been generated from.
    newNamesToOldNames = {}
    # In light of the creation of new regions, we update the region to
    # zone extents map.
    newRegionZoneExtents = {}

    quadricRegionBodyExtentMap = _makeQuadricRegionBodyExtentMap(
        flukareg, quadricRegionExtents)
    for name, region in flukareg.regionDict.items():

        if name not in regions:
            continue
        if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            newNamesToOldNames[name] = name
            newRegionZoneExtents[name] = regionZoneExtents[name]
            continue

        connected_zones = region.connectedZones(
            zoneExtents=regionZoneExtents[name],
            referenceExtent=quadricRegionBodyExtentMap)

        if len(connected_zones) == 1: # then there are no disjoint unions
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            newNamesToOldNames[name] = name
            newRegionZoneExtents[name] = regionZoneExtents[name]
            continue

        for connection in connected_zones: # loop over the connections
            # make new region with appropriate name
            zones_string = "_".join(map(str, connection))
            new_region_name = "{}_djz{}".format(name, zones_string)
            new_region = fluka.Region(new_region_name, material=region.material)
            newNamesToOldNames[new_region_name] = name
            # get the zones which are connected
            zones = [(i, region.zones[i]) for i in connection]
            zoneExtents = [regionZoneExtents[name][i] for i in connection]
            newRegionZoneExtents[new_region_name] = zoneExtents

            for index, zone in zones:
                # copy teh zone, give it a new name since it now
                # belongs to a different region.
                new_zone = deepcopy(zone)
                new_zone.name = "{}_djz_z{}".format(new_zone.name, index)
                new_region.addZone(new_zone)
                new_region.allBodiesToRegistry(fluka_reg_out)
                fluka_reg_out.addRegion(new_region)
    _copyStructureToNewFlukaRegistry(flukareg, fluka_reg_out)

    return fluka_reg_out, newNamesToOldNames, newRegionZoneExtents

def _getRegionZoneExtents(flukareg, regions, quadricRegionExtents):
    """Loop over the regions, and for each region, get all the extents
    of the zones belonging to that region.  Don't do this for
    quadricRegionExtents, instead, just continue to use the extent
    provided by the user."""

    regionZoneExtents = {}
    for name, region in flukareg.regionDict.items():
        if name in quadricRegionExtents:
            # We choose to use the quadricRegionExtents rather than
            # calculate new ones as each quadric must be evaluated
            # with exactly the same extent in all its uses.  E.g if a
            # region consists of a QUA subtraction, and another region
            # consists of that same QUA being used to fill the gap,
            # then if the extents aren't identical, then the two QUA
            # curves won't be perfectly flush against each other, but
            # instead will overlap quite badly.

            # This could be improved by indeed meshing the regions and
            # zones with QUAs in them, for all regions in which a
            # given QUA occurs, return the total enveloping extent.
            # This will give a tighter mesh whilst still ensuring that
            # filling -QUA with +QUA will still work.  However, this
            # is much simpler, and still works reasonably well.
            nzones = len(region.zones)
            regionZoneExtents[name] = nzones * [quadricRegionExtents[name]]
            continue
        elif name not in regions:
            continue
        else:
            regionZoneExtents[name] = region.zoneExtents(referenceExtent=None)
    return regionZoneExtents

def _makeBodyMinimumReferenceExtentMap(flukareg, regionZoneExtents, regions):
    bodies_to_regions = flukareg.getBodyToRegionsMap()
    regionExtents = _regionZoneExtentsToRegionExtents(regionZoneExtents)

    bodies_to_minimum_extents = {}
    for body_name, region_names in bodies_to_regions.items():
        logger.debug("Getting minimum extent for body: %s", body_name)

        bodyRegionExtents = []
        for region_name in region_names:
            if region_name not in regions:
                continue
            bodyRegionExtents.append(regionExtents[region_name])

        if len(regionExtents) == 1:
            extent = list(regionExtents.values())[0]
        elif len(regionExtents) > 1:
            extent = reduce(_getMaximalOfTwoExtents, bodyRegionExtents)
            logger.debug("Minimum extent = %s", extent)
        else:
            raise ValueError("WHAT?")

        bodies_to_minimum_extents[body_name] = extent

    return bodies_to_minimum_extents

def _getMaximalOfTwoExtents(extent1, extent2):
    """Given two extents, returns the total extent that tightly bounds
    the two given extents.

    :param extent1: The first extent.
    :type extent1: Extent
    :param extent2: The second extent
    :type extent2: Extent

    """
    # Get combined extents which are greatest
    lower = [min(a, b) for a, b in zip(extent1.lower, extent2.lower)]
    upper = [max(a, b) for a, b in zip(extent1.upper, extent2.upper)]
    return fluka.Extent(lower, upper)

def _filterBlackHoleRegions(flukareg, regions):
    """Returns a new FlukaRegistry instance with all regions with
    BLKCHOLE material removed.

    :param flukareg: The FlukaRegistry instance from which the new \
    FlukaRegistry instance sans BLCKHOLE regions is built.
    :type flukareg: FlukaRegistry
    :param regions: The names of the regions to be copied to the new \
    instance.
    :type regions: list

    """
    freg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.items():
        try:
            materialName = flukareg.assignmas[name]
        except KeyError: # Ignore assignments to regions that are undefined.
            continue
        if materialName == "BLCKHOLE":
            continue
        if name not in regions:
            continue
        freg_out.addRegion(region)
        region.allBodiesToRegistry(freg_out)
    _copyStructureToNewFlukaRegistry(flukareg, freg_out)
    return freg_out

def _getOverlappingExtents(extent, extents):
    overlappingExtents = []
    for name, e in extents.items():
        if areExtentsOverlapping(extent, e):
            overlappingExtents.append(name)
    return overlappingExtents

def _getContentsOfLatticeCells(flukaregistry, regionExtents):
    regions = flukaregistry.regionDict

    cellContents = {}
    for cellName, lattice in flukaregistry.latticeDict.items():
        transformedCellExtent = _getTransformedCellRegionExtent(lattice)

        overlappingExents = _getOverlappingExtents(transformedCellExtent,
                                                   regionExtents)
        cellContents[cellName] = []
        for regionName in overlappingExents:
            region = regions[regionName]
            overlapping = _isTransformedCellRegionIntersectingWithRegion(
                region, lattice)
            if overlapping:
                cellContents[cellName].append(regionName)

    return cellContents

def _getTransformedCellRegionExtent(lattice):
    # Move the lattice cell region onto the prototype region.
    transform = lattice.getTransform()
    cellRegion = deepcopy(lattice.cellRegion)


    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))
    cellName = cellRegion.name

    greg = g4.Registry()
    wlv = _makeWorldVolume(WORLD_DIMENSIONS, "G4_Galactic", greg)


    region_solid = cellRegion.geant4Solid(greg, referenceExtent=None)
    regionLV = g4.LogicalVolume(region_solid,
                                 "G4_Galactic",
                                 "{}_lv".format(cellName),
                                 greg)

    lower, upper = regionLV.mesh.getBoundingBox(cellRotation,
                                                cellCentre)
    return fluka.Extent(lower, upper)

def _isTransformedCellRegionIntersectingWithRegion(region, lattice):
    cellRegion = deepcopy(lattice.cellRegion)

    transform = lattice.getTransform()

    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))

    # XXX: Nasty hack to get the cellRegion to return the rotation and
    # centre that I want it to return.  These two lines save me a lot
    # of work elsewhere.
    def rotation(self): return cellRotation
    def centre(self, referenceExtent=None): return cellCentre
    cellRegion.rotation = types.MethodType(rotation, cellRegion)
    cellRegion.centre = types.MethodType(centre, cellRegion)

    return areOverlapping(cellRegion, region)

def _checkQuadricRegionExtents(flukareg, quadricRegionExtents):
    """Loop over the regions looking for quadrics and for any quadrics we
    find, make sure that that whregion has a defined region extent in
    quadricRegionExtents.

    """
    for regionName, region in flukareg.regionDict.items():
        regionBodies = region.bodies()
        quadrics = {r for r in regionBodies if isinstance(r, fluka.QUA)}

        # If this region has no Quadrics then all is well
        if not quadrics:
            continue
        elif quadricRegionExtents is None:
            msg = "quadricRegionExtents must be set for regions with QUAs."
            raise ValueError(msg)
        elif regionName in quadricRegionExtents:
            continue

        raise ValueError(
            "QUA region missing from quadricRegionExtents: {}".format(
                regionName))

def _getWorldDimensions(worldDimensions):
    """Get world dimensinos and if None then return the global constant
    WORLD_DIMENSIONS.

    """
    if worldDimensions is None:
        return WORLD_DIMENSIONS
    return worldDimensions

def _getSelectedRegions(flukareg, regions, omitRegions):
    if not flukareg.regionDict:
        raise ValueError("No regions in registry.")
    elif regions and omitRegions:
        raise ValueError("Only one of regions and omitRegions may be set.")
    elif omitRegions:
        return set(flukareg.regionDict).difference(omitRegions)
    elif regions is None:
        return list(flukareg.regionDict)
    return regions

def _filterHalfSpaces(flukareg, regionZoneExtents):
    """Filter redundant half spaces from the regions of the
    FlukaRegistry instance.  Extents is a dictionary of region names
    to region extents."""
    fout = fluka.FlukaRegistry()
    logger.debug("Filtering half spaces")

    regionExtents = _regionZoneExtentsToRegionExtents(regionZoneExtents)

    for region_name, region in flukareg.regionDict.items():
        regionOut = deepcopy(region)
        regionExtent = regionExtents[region_name]
        # Loop over the bodies of this region
        for body in regionOut.bodies():
            # Only potentially omit half spaces
            if isinstance(body, (fluka.XYP, fluka.XZP,
                                 fluka.YZP, fluka.PLA)):
                normal, pointOnPlane = body.toPlane()
                extentCornerDistance = regionExtent.cornerDistance()
                d = _distanceFromPointToPlane(normal, pointOnPlane,
                                              regionExtent.centre)
                # If the distance from the point on the plane closest
                # to the centre of the extent is greater than the
                # maximum distance from centre to corner, then we
                # remove it (accounting for some tolerance) from the
                # region.
                if d > 1.025 * extentCornerDistance:
                    logger.debug(
                        ("Filtering %s from region %s."
                         "  extent = %s, extentMax = %s, d=%s"),
                        body, region_name, regionExtent,
                        extentCornerDistance, d)
                    regionOut.removeBody(body.name)
        # add this region to the output fluka registry along with the
        # filtered bodies.
        fout.addRegion(regionOut)
        regionOut.allBodiesToRegistry(fout)

    _copyStructureToNewFlukaRegistry(flukareg, fout)

    return fout

def _distanceFromPointToPlane(normal, pointOnPlane, point):
    normal = fluka.Three(normal).unit()
    return abs(np.dot(normal, point - pointOnPlane))

def _convertLatticeCells(greg, flukareg, wlv, regionZoneExtents,
                         regionNamesToLVs):
    regionExtents = _regionZoneExtentsToRegionExtents(regionZoneExtents)


    # If no lattices defined then we end the conversion here.
    latticeContents = _getContentsOfLatticeCells(flukareg, regionExtents)
    for latticeName, contents in latticeContents.items():
        # We take the LVs associated with this lattice (which have been
        # placed above as PV) and place it with the translation and
        # rotation of the lattice cell.
        cellRegion = flukareg.latticeDict[latticeName].cellRegion
        cellCentre = list(cellRegion.centre())
        cellRotation = list(trans.reverse(cellRegion.tbxyz()))

        for prototypeName in contents:
            prototypeLV = regionNamesToLVs[prototypeName]
            g4.PhysicalVolume(cellRotation,
                              cellCentre,
                              prototypeLV,
                              "{}_lattice_pv".format(latticeName),
                              wlv, greg)

def _makeUniqueQuadricRegions(flukareg, quadricRegionExtents):
    quadricRegionExtents = _getMaximalQuadricRegionExtents(
        flukareg,
        quadricRegionExtents)

    bodiesToRegions = flukareg.getBodyToRegionsMap()
    flukaRegOut = fluka.FlukaRegistry()
    for regionName, region in flukareg.regionDict.items():
        if regionName in quadricRegionExtents:
            uniqueRegion = region.makeUnique("_"+regionName, flukaRegOut)
            flukaRegOut.addRegion(uniqueRegion)
        else:
            newRegion = deepcopy(region)
            flukaRegOut.addRegion(newRegion)
            newRegion.allBodiesToRegistry(flukaRegOut)

    _copyStructureToNewFlukaRegistry(flukareg, flukaRegOut)
    return flukaRegOut

def _makeQuadricRegionBodyExtentMap(flukareg, quadricRegionExtents):
    """Given a map of regions featuring quadrics to their extents, we
    loop over the bodies of the region and set their extents equal to
    the region extent."""
    if quadricRegionExtents is None:
        return {}
    if quadricRegionExtents is not None:
        quadricRegionBodyExtentMap = {}
        for regionName, extent in quadricRegionExtents.items():
            if regionName not in flukareg.regionDict:
                continue
            for body in flukareg.regionDict[regionName].bodies():
                quadricRegionBodyExtentMap[body.name] = extent
        return quadricRegionBodyExtentMap

def _getMaximalQuadricRegionExtents(freg, quadricRegionExtents):
    # Loop over the regions.  If a QUA in this region is present in
    # another region, then do max(currentExtent, otherExtent) for this
    # region's extent.
    if not quadricRegionExtents:
        return {}

    regionSharedExtents = {}
    bodiesToRegions = freg.getBodyToRegionsMap()
    for regionName, regionExtent in quadricRegionExtents.items():
        region = freg.regionDict[regionName]
        for body in region.bodies():
            if not isinstance(body, fluka.QUA):
                continue

            regionSharedExtents[regionName] = regionExtent
            otherRegions = bodiesToRegions[body.name]
            for otherRegion in otherRegions:
                if otherRegion in quadricRegionExtents:
                    otherExtent = quadricRegionExtents[otherRegion]
                    currentExtent = regionSharedExtents[regionName]
                    regionSharedExtents[regionName] = \
                        _getMaximalOfTwoExtents(otherExtent, currentExtent)
    return regionSharedExtents

def _regionZoneExtentsToRegionExtents(regionZoneExtents):
    """Given a map of region names to zone extents, return a map of
    region names to a total region extent."""
    regionExtents = {}
    for name, zoneExtents in regionZoneExtents.items():
        regionExtent = reduce(_getMaximalOfTwoExtents,
                              zoneExtents,
                              zoneExtents[0])
        regionExtents[name] = regionExtent
    return regionExtents


def _copyStructureToNewFlukaRegistry(freg, fregtarget):
    fregtarget.latticeDict = deepcopy(freg.latticeDict)
    fregtarget.assignmas = deepcopy(freg.assignmas)
    fregtarget.materials = deepcopy(freg.materials)
