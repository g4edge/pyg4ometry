import logging
from copy import deepcopy
import warnings
import types

import numpy as np

import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans
from pyg4ometry.fluka.vector import (Extent, areExtentsOverlapping)
from pyg4ometry.fluka.region import areOverlapping
from pyg4ometry.fluka import Transform


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
    :param materialMap: Dictionary of FLUKA material names to Geant4 \
    materials used to determine the materials of the resulting geometry.
    :type materialMap: dict
    :param omitRegions: Names of regions to be omitted from the \
    conversion.  This option is mutually exclusive with the kwarg regions.
    :type omitRegions: list
    :param quadricRegionExtents: The axis-aligned extents of any regions \
    featuring QUA bodies, mapping region names to fluka.Extent instances.
    :type quadricRegionExtents: dict

    """

    # Bomb if we have quadrics but no quadricReferenceExtents
    quadricRegionExtents = _checkQuadricRegionExtents(flukareg,
                                                      quadricRegionExtents)
    quadricRegionExtents = _getMaximalQuadricRegionExtents(flukareg,
                                                           quadricRegionExtents)

    # If we have quadricReferenceExtents then use them
    if quadricRegionExtents:
        flukareg = _makeUniqueQuadricRegions(flukareg, quadricRegionExtents)

    # Filter on selected regions (regions and omitRegions)
    regions = _getSelectedRegions(flukareg, regions, omitRegions)

    # Filter BLCKHOLE regions from the FlukaRegistry
    if omitBlackholeRegions:
        flukareg = _filterBlackHoleRegions(flukareg, regions)

    # Make a new FlukaRegistry with length safety applied to all of
    # the regions.
    if withLengthSafety:
        flukareg = _makeLengthSafetyRegistry(flukareg, regions)
    # set world dimensions
    worldDimensions = _getWorldDimensions(worldDimensions)

    # Split disjoint unions into their constituents.
    if splitDisjointUnions:
        # print 'splitDisjointUnions'
        flukareg, newNamesToOldNames = _makeDisjointUnionsFlukaRegistry(
            flukareg, regions, quadricRegionExtents)

        newRegions = []
        newQuadricRegionExtents = {}
        for newName, oldName in newNamesToOldNames.iteritems():
            if oldName in regions:
                newRegions.append(newName)
            if oldName in quadricRegionExtents:
                newQuadricRegionExtents[newName] = quadricRegionExtents[oldName]

        regions = newRegions
        quadricRegionExtents = newQuadricRegionExtents

    # Do infinite solid minimisation
    referenceExtentMap = None
    if minimiseSolids:
        # print 'minimiseSolids'
        regionExtents = _getRegionExtents(flukareg, regions,
                                          quadricRegionExtents)
        referenceExtentMap = _makeBodyMinimumReferenceExtentMap(flukareg,
                                                                regionExtents,
                                                                regions)
        flukareg = _filterHalfSpaces(flukareg, regionExtents)


    # With the modified fluka registry, finally, we convert to Geant4:
    greg = g4.Registry()
    wlv = _makeWorldVolume(worldDimensions, worldMaterial, greg)

    materialMap = {} if materialMap is None else materialMap
    regionsToLVs = {} # For possible convertion of LATTICEs
    # Do non-lattice regions first as we convert the lattices in the
    # loop after this, as they must be treated differently.
    for name, region in flukareg.regionDict.iteritems():
        if name not in regions:
            continue

        # print name
        region = flukareg.regionDict[name]
        region_solid = region.geant4Solid(greg,
                                          referenceExtent=referenceExtentMap)

        region_material = region.material
        if region_material is None:
            warnings.warn(
                "Setting None material in region {} to G4_Fe.".format(
                    name))
            region_material = g4.MaterialPredefined("G4_Fe")

        elif region_material in materialMap:
            region_material = materialMap[region_material]
        else:
            region_material = g4.MaterialPredefined("G4_Fe")

        region_lv = g4.LogicalVolume(region_solid,
                                     region_material,
                                     "{}_lv".format(name),
                                     greg)

        regionsToLVs[name] = region_lv
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

    _convertLatticeCells(greg, flukareg, wlv, regionExtents, regionsToLVs)
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
    fluka_reg_out.latticeDict = deepcopy(flukareg.latticeDict)

    return fluka_reg_out

def _makeDisjointUnionsFlukaRegistry(flukareg, regions, quadricRegionExtents):
    fluka_reg_out = fluka.FlukaRegistry()
    newNamesToOldNames = {}

    quadricRegionBodyExtentMap = _makeQuadricRegionBodyExtentMap(
        flukareg, quadricRegionExtents)
    for name, region in flukareg.regionDict.iteritems():

        if name not in regions:
            continue
        if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
            new_region = deepcopy(region)
            fluka_reg_out.addRegion(new_region)
            new_region.allBodiesToRegistry(fluka_reg_out)
            newNamesToOldNames[name] = name
            continue

        connected_zones = region.connectedZones(
            zoneExtents=regionZoneExtents[name],
            referenceExtent=quadricRegionBodyExtentMap)

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
    fluka_reg_out.latticeDict = deepcopy(flukareg.latticeDict)

    return fluka_reg_out, newNamesToOldNames

def _getRegionExtents(flukareg, regions, quadricRegionExtents):
    regionmap = flukareg.regionDict
    regionExtents = {}
    referenceExtent = None
    if quadricRegionExtents:
        referenceExtent = _makeQuadricRegionBodyExtentMap(flukareg,
                                                          quadricRegionExtents)
    for name, region in regionmap.iteritems():
        if name in quadricRegionExtents:
            regionExtents[name] = quadricRegionExtents[name]

        if name not in regions:
            continue
        regionExtents[name] = region.extent(referenceExtent=referenceExtent)
    # XXX: We choose to use the quadricRegionExtents rather than the
    # newly caclulated ones as each quadric must be evaluated with
    # exactly the same extent in all its uses.  Could go again with
    # getMaximalQuadricRegionExtents here, and ideally would.
    regionExtents.update(quadricRegionExtents)
    return regionExtents

def _makeBodyMinimumReferenceExtentMap(flukareg, regionExtents, regions):
    bodies_to_regions = flukareg.getBodyToRegionsMap()

    bodies_to_minimum_extents = {}
    for body_name, region_names in bodies_to_regions.iteritems():
        logger.debug("Getting minimum extent for body: %s", body_name)

        bodyRegionExtents = []
        for region_name in region_names:
            if region_name not in regions:
                continue
            bodyRegionExtents.append(regionExtents[region_name])

        if len(regionExtents) == 1:
            extent = regionExtents.values()[0]
        elif len(regionExtents) > 1:
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

def _filterBlackHoleRegions(flukareg, regions):

    freg_out = fluka.FlukaRegistry()
    for name, region in flukareg.regionDict.iteritems():
        if region.material == "BLCKHOLE":
            continue
        if name not in regions:
            continue
        freg_out.addRegion(region)
        region.allBodiesToRegistry(freg_out)
    freg_out.latticeDict = deepcopy(flukareg.latticeDict)
    return freg_out

def _getOverlappingExtents(extent, extents):
    overlappingExtents = []
    for name, e in extents.iteritems():
        if areExtentsOverlapping(extent, e):
            overlappingExtents.append(name)
    return overlappingExtents

def _getContentsOfLatticeCells(flukaregistry, regionExtents):
    regions = flukaregistry.regionDict

    cellContents = {}
    for cellName, lattice in flukaregistry.latticeDict.iteritems():
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
    for regionName, region in flukareg.regionDict.iteritems():
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
    if not quadricRegionExtents:
        return {}
    return quadricRegionExtents



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

def _filterHalfSpaces(flukareg, extents):
    """Filter redundant half spaces from the regions of the
    FlukaRegistry instance.  Extents is a dictionary of region names
    to region extents."""
    fout = fluka.FlukaRegistry()
    logger.debug("Filtering half spaces")

    for region_name, region in flukareg.regionDict.iteritems():
        regionOut = deepcopy(region)
        regionExtent = extents[region_name]
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

    fout.latticeDict = deepcopy(flukareg.latticeDict)

    return fout

def _distanceFromPointToPlane(normal, pointOnPlane, point):
    normal = fluka.Three(normal).unit()
    return abs(np.dot(normal, point - pointOnPlane))

def _convertLatticeCells(greg, flukareg, wlv, regionExtents, regionsToLVs):
    # If no lattices defined then we end the conversion here.
    latticeContents = _getContentsOfLatticeCells(flukareg, regionExtents)
    for latticeName, contents in latticeContents.iteritems():
        # We take the LVs associated with this lattice (which have been
        # placed above as PV) and place it with the translation and
        # rotation of the lattice cell.
        cellRegion = flukareg.latticeDict[latticeName].cellRegion
        cellCentre = list(cellRegion.centre())
        cellRotation = list(trans.reverse(cellRegion.tbxyz()))

        for prototypeName in contents:
            prototypeLV = regionsToLVs[prototypeName]
            g4.PhysicalVolume(cellRotation,
                              cellCentre,
                              prototypeLV,
                              "{}_lattice_pv".format(latticeName),
                              wlv, greg)

def _makeUniqueQuadricRegions(flukareg, quadricRegionExtents):
    bodiesToRegions = flukareg.getBodyToRegionsMap()
    flukaRegOut = fluka.FlukaRegistry()
    for regionName, region in flukareg.regionDict.iteritems():
        if regionName in quadricRegionExtents:
            uniqueRegion = region.makeUnique("_"+regionName, flukaRegOut)
            flukaRegOut.addRegion(uniqueRegion)
        else:
            newRegion = deepcopy(region)
            flukaRegOut.addRegion(newRegion)
            newRegion.allBodiesToRegistry(flukaRegOut)


    flukaRegOut.latticeDict = flukareg.latticeDict
    return flukareg

def _makeQuadricRegionBodyExtentMap(flukareg, quadricRegionExtents):
    """Given a map of regions featuring quadrics to their extents, we
    loop over the bodies of the region and set their extents equal to
    the region extent."""
    if quadricRegionExtents is None:
        return {}
    if quadricRegionExtents is not None:
        quadricRegionBodyExtentMap = {}
        for regionName, extent in quadricRegionExtents.iteritems():
            if regionName not in flukareg.regionDict:
                continue
            for body in flukareg.regionDict[regionName].bodies():
                quadricRegionBodyExtentMap[body.name] = extent
        return quadricRegionBodyExtentMap

def _getMaximalQuadricRegionExtents(freg, quadricRegionExtents):
    # Loop over the regions.  If a QUA in this region is present in
    # another region, then do max(currentExtent, otherExtent) for this
    # region's extent.

    regionSharedExtents = {}
    bodiesToRegions = freg.getBodyToRegionsMap()
    for regionName, regionExtent in quadricRegionExtents.iteritems():
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
