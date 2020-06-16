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
from pyg4ometry.fluka.vector import (AABB, areAABBsOverlapping)
from pyg4ometry.exceptions import FLUKAError
import pyg4ometry.fluka as fluka
import pyg4ometry.geant4 as g4
import pyg4ometry.transformation as trans
from pyg4ometry.utils import Timer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WORLD_DIMENSIONS = [10000, 10000, 10000]

def fluka2Geant4(flukareg,
                 regions=None,
                 withLengthSafety=True,
                 minimiseSolids=True,
                 worldMaterial="G4_Galactic",
                 worldDimensions=None,
                 omitBlackholeRegions=True,
                 omitRegions=None,
                 quadricRegionAABBs=None,
                 **kwargs):
    """Convert a FLUKA registry to a Geant4 Registry.

    :param flukareg: FlukaRegistry instance to be converted.
    :type flukareg: FlukaRegistry
    :param regions: Names of regions to be converted, by default \
    all are converted.  Mutually exclusive with omitRegions.
    :type regions: list
    :param withLengthSafety: Whether or not to apply automatic length safety.
    :type withLengthSafety: bool
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
    :param quadricRegionAABBs: The axis-aligned aabbs of any regions \
    featuring QUA bodies, mapping region names to fluka.AABB instances.
    :type quadricRegionAABBs: dict

    """
    fr = flukareg # abbreviation

    timer = kwargs.get("timer", Timer())
    timer.update()

    regions = _getSelectedRegions(fr, regions, omitRegions)
    if omitBlackholeRegions:
        fr = _filterBlackHoleRegions(fr, regions)

    _checkQuadricRegionAABBs(fr, quadricRegionAABBs)

    if quadricRegionAABBs:
        fr = _makeUniqueQuadricRegions(fr, quadricRegionAABBs)
    else:
        quadricRegionAABBs = {}

    if withLengthSafety:
        timer.update()
        fr = _makeLengthSafetyRegistry(fr, regions)
        timer.add("length safety")

    if minimiseSolids:
        regionZoneAABBs = _getRegionZoneAABBs(fr, regions, quadricRegionAABBs)
        timer.add("zone aabbs")

    aabbMap = None
    if minimiseSolids:
        aabbMap = _makeBodyMinimumAABBMap(fr, regionZoneAABBs, regions)
        fr = _filterHalfSpaces(fr, regionZoneAABBs)
        timer.add("solid minimisation")

    # This loop below do the main conversion
    greg = g4.Registry()
    f2g4mat = makeFlukaToG4MaterialsMap(fr, greg)
    timer.add("materials")
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
        region_solid = region.geant4Solid(greg, aabb=aabbMap)

        try:
            materialName = assignmas[name]
        except KeyError:
            warnings.warn(f"Setting region {name} with no material to IRON.")
            materialName = "IRON"

        material = f2g4mat[materialName]

        region_lv = g4.LogicalVolume(region_solid, material, f"{name}_lv", greg)

        regionNamesToLVs[name] = region_lv
        # We reverse because rotations in the context of Booleans are
        # active, and that is the convention we have followed so far,
        # but volume rotations are passive, so we have to reverse the
        # rotation.
        rot = list(trans.reverse(region.tbxyz()))
        g4.PhysicalVolume(
            rot,
            list(region.centre(aabb=aabbMap)),
            region_lv,
            f"{name}_pv",
            wlv, greg)
    timer.add("main loop")
    timer.updateTotal()
    _convertLatticeCells(greg, fr, wlv, regionZoneAABBs, regionNamesToLVs)
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

def _getRegionZoneAABBs(flukareg, regions, quadricRegionAABBs):
    """Loop over the regions, and for each region, get all the aabbs
    of the zones belonging to that region.  Don't do this for
    quadricRegionAABBs, instead, just continue to use the aabb
    provided by the user."""

    regionZoneAABBs = {}
    for name, region in flukareg.regionDict.items():
        if name in quadricRegionAABBs:
            # We choose to use the quadricRegionAABBs rather than
            # calculate new ones as each quadric must be evaluated
            # with exactly the same aabb in all its uses.  E.g if a
            # region consists of a QUA subtraction, and another region
            # consists of that same QUA being used to fill the gap,
            # then if the aabbs aren't identical, then the two QUA
            # curves won't be perfectly flush against each other, but
            # instead will overlap quite badly.

            # This could be improved by indeed meshing the regions and
            # zones with QUAs in them, for all regions in which a
            # given QUA occurs, return the total enveloping aabb.
            # This will give a tighter mesh whilst still ensuring that
            # filling -QUA with +QUA will still work.  However, this
            # is much simpler, and still works reasonably well.
            nzones = len(region.zones)
            regionZoneAABBs[name] = nzones * [quadricRegionAABBs[name]]
            continue
        elif name not in regions:
            continue
        else:
            regionZoneAABBs[name] = region.zoneAABBs(aabb=None)
    return regionZoneAABBs

def _makeBodyMinimumAABBMap(flukareg, regionZoneAABBs, regions):
    bodies_to_regions = flukareg.getBodyToRegionsMap()
    regionAABBs = _regionZoneAABBsToRegionAABBs(regionZoneAABBs)

    bodies_to_minimum_aabbs = {}
    for body_name, region_names in bodies_to_regions.items():
        logger.debug("Getting minimum aabb for body: %s", body_name)

        bodyRegionAABBs = []
        for region_name in region_names:
            if region_name not in regions:
                continue
            bodyRegionAABBs.append(regionAABBs[region_name])

        if len(regionAABBs) == 1:
            aabb = list(regionAABBs.values())[0]
        elif len(regionAABBs) > 1:
            aabb = reduce(_getMaximalOfTwoAABBs, bodyRegionAABBs)
            logger.debug("Minimum aabb = %s", aabb)
        else:
            raise ValueError("WHAT?")

        bodies_to_minimum_aabbs[body_name] = aabb

    return bodies_to_minimum_aabbs

def _getMaximalOfTwoAABBs(aabb1, aabb2):
    """Given two aabbs, returns the total aabb that tightly bounds
    the two given aabbs.

    :param aabb1: The first aabb.
    :type aabb1: AABB
    :param aabb2: The second aabb
    :type aabb2: AABB

    """
    return aabb1.union(aabb2)


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
        if name not in flukareg.assignmas and name in regions:
            freg_out.addRegion(region) # add region even if no assigned material
            region.allBodiesToRegistry(freg_out)
        elif name not in regions:
            continue
        elif flukareg.assignmas[name] == "BLCKHOLE":
            continue
        else:
            freg_out.addRegion(region) # add region even if no assigned material
            region.allBodiesToRegistry(freg_out)
    _copyStructureToNewFlukaRegistry(flukareg, freg_out)
    return freg_out

def _getOverlappingAABBs(aabb, aabbs):
    overlappingAABBs = []
    for name, e in aabbs.items():
        if areAABBsOverlapping(aabb, e):
            overlappingAABBs.append(name)
    return overlappingAABBs

def _getContentsOfLatticeCells(flukaregistry, regionAABBs):
    regions = flukaregistry.regionDict

    cellContents = {}
    for cellName, lattice in flukaregistry.latticeDict.items():
        transformedCellAABB = _getTransformedCellRegionAABB(lattice)

        overlappingExents = _getOverlappingAABBs(transformedCellAABB,
                                                   regionAABBs)
        cellContents[cellName] = []
        for regionName in overlappingExents:
            region = regions[regionName]
            overlapping = _isTransformedCellRegionIntersectingWithRegion(
                region, lattice)
            if overlapping:
                cellContents[cellName].append(regionName)

    return cellContents

def _getTransformedCellRegionAABB(lattice):
    # Move the lattice cell region onto the prototype region.
    transform = lattice.getTransform()
    cellRegion = deepcopy(lattice.cellRegion)


    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))
    cellName = cellRegion.name

    greg = g4.Registry()
    wlv = _makeWorldVolume(WORLD_DIMENSIONS, "G4_Galactic", greg)


    region_solid = cellRegion.geant4Solid(greg, aabb=None)
    regionLV = g4.LogicalVolume(region_solid,
                                 "G4_Galactic",
                                 f"{cellName}_lv",
                                 greg)

    lower, upper = regionLV.mesh.getBoundingBox(cellRotation,
                                                cellCentre)
    return fluka.AABB(lower, upper)

def _isTransformedCellRegionIntersectingWithRegion(region, lattice):
    cellRegion = deepcopy(lattice.cellRegion)

    transform = lattice.getTransform()

    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))

    # XXX: Nasty hack to get the cellRegion to return the rotation and
    # centre that I want it to return.  These two lines save me a lot
    # of work elsewhere.
    def rotation(self): return cellRotation
    def centre(self, aabb=None): return cellCentre
    cellRegion.rotation = types.MethodType(rotation, cellRegion)
    cellRegion.centre = types.MethodType(centre, cellRegion)

    return areOverlapping(cellRegion, region)

def _checkQuadricRegionAABBs(flukareg, quadricRegionAABBs):
    """Loop over the regions looking for quadrics and for any quadrics we
    find, make sure that that whregion has a defined region aabb in
    quadricRegionAABBs.

    """
    for regionName, region in flukareg.regionDict.items():
        regionBodies = region.bodies()
        quadrics = {r for r in regionBodies if isinstance(r, fluka.QUA)}

        # If this region has no Quadrics then all is well
        if not quadrics:
            continue
        elif quadricRegionAABBs is None:
            msg = "quadricRegionAABBs must be set for regions with QUAs."
            raise ValueError(msg)
        elif regionName in quadricRegionAABBs:
            continue

        raise ValueError(
            f"QUA region missing from quadricRegionAABBs: {regionName}")

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

def _filterHalfSpaces(flukareg, regionZoneAABBs):
    """Filter redundant half spaces from the regions of the
    FlukaRegistry instance.  AABBs is a dictionary of region names
    to region aabbs."""
    fout = fluka.FlukaRegistry()
    logger.debug("Filtering half spaces")

    regionAABBs = _regionZoneAABBsToRegionAABBs(regionZoneAABBs)

    for region_name, region in flukareg.regionDict.items():
        regionOut = deepcopy(region)
        regionAABB = regionAABBs[region_name]
        # Loop over the bodies of this region
        for body in regionOut.bodies():
            # Only potentially omit half spaces
            if isinstance(body, (fluka.XYP, fluka.XZP,
                                 fluka.YZP, fluka.PLA)):
                normal, pointOnPlane = body.toPlane()
                aabbCornerDistance = regionAABB.cornerDistance()
                d = _distanceFromPointToPlane(normal, pointOnPlane,
                                              regionAABB.centre)
                # If the distance from the point on the plane closest
                # to the centre of the aabb is greater than the
                # maximum distance from centre to corner, then we
                # remove it (accounting for some tolerance) from the
                # region.
                if d > 1.025 * aabbCornerDistance:
                    logger.debug(
                        ("Filtering %s from region %s."
                         "  aabb = %s, aabbMax = %s, d=%s"),
                        body, region_name, regionAABB,
                        aabbCornerDistance, d)
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

def _convertLatticeCells(greg, flukareg, wlv, regionZoneAABBs,
                         regionNamesToLVs):
    regionAABBs = _regionZoneAABBsToRegionAABBs(regionZoneAABBs)

    # If no lattices defined then we end the conversion here.
    latticeContents = _getContentsOfLatticeCells(flukareg, regionAABBs)
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
                              f"{latticeName}_lattice_pv",
                              wlv, greg)

def _makeUniqueQuadricRegions(flukareg, quadricRegionAABBs):
    quadricRegionAABBs = _getMaximalQuadricRegionAABBs(
        flukareg,
        quadricRegionAABBs)

    bodiesToRegions = flukareg.getBodyToRegionsMap()
    flukaRegOut = fluka.FlukaRegistry()
    for regionName, region in flukareg.regionDict.items():
        if regionName in quadricRegionAABBs:
            uniqueRegion = region.makeUnique("_"+regionName, flukaRegOut)
            flukaRegOut.addRegion(uniqueRegion)
        else:
            newRegion = deepcopy(region)
            flukaRegOut.addRegion(newRegion)
            newRegion.allBodiesToRegistry(flukaRegOut)

    _copyStructureToNewFlukaRegistry(flukareg, flukaRegOut)
    return flukaRegOut

def _makeQuadricRegionBodyAABBMap(flukareg, quadricRegionAABBs):
    """Given a map of regions featuring quadrics to their aabbs, we
    loop over the bodies of the region and set their aabbs equal to
    the region aabb."""
    if quadricRegionAABBs is None:
        return {}
    if quadricRegionAABBs is not None:
        quadricRegionBodyAABBMap = {}
        for regionName, aabb in quadricRegionAABBs.items():
            if regionName not in flukareg.regionDict:
                continue
            for body in flukareg.regionDict[regionName].bodies():
                quadricRegionBodyAABBMap[body.name] = aabb
        return quadricRegionBodyAABBMap

def _getMaximalQuadricRegionAABBs(freg, quadricRegionAABBs):
    # Loop over the regions.  If a QUA in this region is present in
    # another region, then do max(currentAABB, otherAABB) for this
    # region's aabb.
    if not quadricRegionAABBs:
        return {}

    regionSharedAABBs = {}
    bodiesToRegions = freg.getBodyToRegionsMap()
    for regionName, regionAABB in quadricRegionAABBs.items():
        region = freg.regionDict[regionName]
        for body in region.bodies():
            if not isinstance(body, fluka.QUA):
                continue

            regionSharedAABBs[regionName] = regionAABB
            otherRegions = bodiesToRegions[body.name]
            for otherRegion in otherRegions:
                if otherRegion in quadricRegionAABBs:
                    otherAABB = quadricRegionAABBs[otherRegion]
                    currentAABB = regionSharedAABBs[regionName]
                    regionSharedAABBs[regionName] = \
                        _getMaximalOfTwoAABBs(otherAABB, currentAABB)
    return regionSharedAABBs

def _regionZoneAABBsToRegionAABBs(regionZoneAABBs):
    """Given a map of region names to zone aabbs, return a map of
    region names to a total region aabb."""
    regionAABBs = {}
    for name, zoneAABBs in regionZoneAABBs.items():
        regionAABB = reduce(_getMaximalOfTwoAABBs,
                              zoneAABBs,
                              zoneAABBs[0])
        regionAABBs[name] = regionAABB
    return regionAABBs


def _copyStructureToNewFlukaRegistry(freg, fregtarget):
    fregtarget.latticeDict = deepcopy(freg.latticeDict)
    fregtarget.assignmas = deepcopy(freg.assignmas)
    fregtarget.materials = deepcopy(freg.materials)
