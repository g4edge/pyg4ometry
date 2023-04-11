from copy import deepcopy as _deepcopy
from collections import namedtuple as _namedtuple
from functools import reduce as _reduce
import logging as _logging
import numpy as _np
import types as _types
import warnings as _warnings

from .fluka2g4materials import makeFlukaToG4MaterialsMap as _makeFlukaToG4MaterialsMap
from pyg4ometry.fluka.vector import areAABBsOverlapping as _areAABBsOverlapping
import pyg4ometry.fluka as _fluka
import pyg4ometry.geant4 as _g4
import pyg4ometry.transformation as _trans

import pyg4ometry.config as _config
if _config.meshing == _config.meshingType.cgal_sm:
    from pyg4ometry.pycgal.core import do_intersect as _do_intersect
elif _config.meshing == _config.meshingType.pycsg:
    from pyg4ometry.pycsg.core import do_intersect as _do_intersect

logger = _logging.getLogger(__name__)
logger.setLevel(_logging.INFO)

WORLD_DIMENSIONS = [10000, 10000, 10000]

class NullModel(Exception): pass

def fluka2Geant4(flukareg,
                 regions=None,
                 omitRegions=None,
                 worldMaterial="G4_Galactic",
                 worldDimensions=None,
                 omitBlackholeRegions=True,
                 quadricRegionAABBs=None,
                 **kwargs):
    """
    Convert a FLUKA registry to a Geant4 Registry.

    :param flukareg: FlukaRegistry instance to be converted.
    :type flukareg: FlukaRegistry
    :param regions: Names of regions to be converted, by default all are converted.  Mutually exclusive with omitRegions.
    :type regions: list
    :param omitRegions: Names of regions to be omitted from the conversion.  This option is mutually exclusive with the kwarg regions.
    :type omitRegions: list
    :param worldMaterial: name of world material to be used.
    :type worldMaterial: string
    :param worldDimensions: dimensions of world logical volume in converted Geant4.  By default this is equal to WORLD_DIMENSIONS.
    :type worldDimensions: list
    :param omitBlackholeRegions: whether or not to omit regions with the FLUKA material BLCKHOLE from the conversion.  By default, true.
    :type omitBlackholeRegions: bool
    :param quadricRegionAABBs: The axis-aligned aabbs of any regions featuring QUA bodies, mapping region names to fluka.AABB instances.
    :type quadricRegionAABBs: dict

    Developer options (to kwargs) withLengthSafety: Whether or not to apply automatic length safety.

    minimiseSolids: Whether or not to minimise the boxes and tubes of Geant4 used to represent infinite solids in FLUKA.

    """

    kwargs.setdefault("minimiseSolids", True)
    kwargs.setdefault("withLengthSafety", True)

    regions = _getSelectedRegions(flukareg, regions, omitRegions)
    if omitBlackholeRegions:
        flukareg = _filterBlackHoleRegions(flukareg, regions)

    _checkQuadricRegionAABBs(flukareg, quadricRegionAABBs)

    if quadricRegionAABBs:
        flukareg = _makeUniqueQuadricRegions(flukareg, quadricRegionAABBs)
    else:
        quadricRegionAABBs = {}

    if kwargs["withLengthSafety"]:
        flukareg = _makeLengthSafetyRegistry(flukareg, regions)

    if kwargs["minimiseSolids"]:
        regionZoneAABBs = _getRegionZoneAABBs(flukareg, regions,
                                              quadricRegionAABBs)
        flukareg, regionZoneAABBs = _filterRegistryNullZones(flukareg,
                                                             regionZoneAABBs)
        regions = [r for r in regions if r in regionZoneAABBs]
        if not regions:
            raise NullModel("Conversion result is null.")

    aabbMap = None
    if kwargs["minimiseSolids"]:
        aabbMap = _makeBodyMinimumAABBMap(flukareg, regionZoneAABBs, regions)
        flukareg = _filterHalfSpaces(flukareg, regionZoneAABBs)

    WorldInfo = _namedtuple("WorldInfo", ["material", "dimensions"])
    worldinfo = WorldInfo(worldMaterial, worldDimensions)

    AABBInfo = _namedtuple("AABBInfo", ["aabbMap", "regionZoneAABBs"])
    aabbinfo = AABBInfo(aabbMap, regionZoneAABBs)

    regions = _filteredRegions(flukareg, regions)

    # After the several steps above transforming the fluka registry, we now
    # take the transformed fluka registry and convert it to a g4 registry.
    return _flukaRegistryToG4Registry(flukareg, regions, worldinfo, aabbinfo)

def _flukaRegistryToG4Registry(flukareg, regions, worldinfo, aabbinfo):
    """
    Convert a transformed fluka registry to a geant4 registry.
    """
    greg = _g4.Registry()
    f2g4mat = _makeFlukaToG4MaterialsMap(flukareg, greg)
    wlv = _makeWorldVolume(_getWorldDimensions(worldinfo.dimensions),
                           worldinfo.material, greg)
    regionNamesToLVs = {}
    for region in regions:
        name = region.name
        region_solid = region.geant4Solid(greg, aabb=aabbinfo.aabbMap)

        try:
            materialName = flukareg.assignmas[name]
        except KeyError:
            _warnings.warn(f"Setting region {name} with no material to IRON.")
            materialName = "IRON"

        material = f2g4mat[materialName]

        region_lv = _g4.LogicalVolume(region_solid, material, f"{name}_lv", greg)

        regionNamesToLVs[name] = region_lv
        # We reverse because rotations in the context of Booleans are
        # active, and that is the convention we have followed so far,
        # but volume rotations are passive, so we have to reverse the
        # rotation.
        rot = list(_trans.reverse(region.tbxyz()))
        _g4.PhysicalVolume(
            rot,
            list(region.centre(aabb=aabbinfo.aabbMap)),
            region_lv,
            f"{name}_pv",
            wlv, greg)
    try:
        _convertLatticeCells(greg, flukareg, wlv,
                             aabbinfo.regionZoneAABBs, regionNamesToLVs)
    except UnboundLocalError:
        pass
    greg.setWorld(wlv.name)

    return greg

def _filteredRegions(flukareg, regions):
    for name, region in flukareg.regionDict.items():
        if name in regions:
            yield region

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
    worldMaterial = _g4.MaterialPredefined(material)

    world_solid = _g4.solid.Box("world_solid",
                               dimensions[0],
                               dimensions[1],
                               dimensions[2], g4registry, "mm")
    wlv = _g4.LogicalVolume(world_solid, worldMaterial, "wl", g4registry)
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
    bigger = _fluka.FlukaRegistry()
    smaller = _fluka.FlukaRegistry()

    for body in flukareg.bodyDict.values():
        bigger.addBody(body.safetyExpanded())
        smaller.addBody(body.safetyShrunk())

    # return bigger, smaller
    fluka_reg_out = _fluka.FlukaRegistry()
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

def _filterRegistryNullZones(flukareg, regionZoneAABBs):
    regout = _deepcopy(flukareg)
    for regionName, aabbs in regionZoneAABBs.items():
        region = regout.regionDict[regionName]
        region.zones = list(_filterRegionNullZones(region, aabbs))
        if not region.zones:
            logger.warn(f"Omitting null region {region.name} from conversion")
            del regout.regionDict[regionName]
            regout.assignmas.pop(regionName, None)

    regionZoneAABBs = _filterNullAABBs(regionZoneAABBs)
    return regout, regionZoneAABBs
    # for name, region in flukareg.regionDict.items():
    #     from IPython import embed; embed()

def _filterRegionNullZones(region, aabbs):
    for zone, aabb in zip(region.zones, aabbs):
        if aabb is not None:
            yield zone
        else:
            logger.warn(
                f"Filtering null zone {zone.dumps()} in region "
                f"{region.name} from conversion")

def _filterNullAABBs(regionZoneAABBs):
    out = {}
    for regionName, aabbs in regionZoneAABBs.items():
        aabbs = [a for a in aabbs if a is not None]
        if aabbs:
            out[regionName] = aabbs
    return out

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
            aabb = _reduce(_getMaximalOfTwoAABBs, bodyRegionAABBs)
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
    freg_out = _fluka.FlukaRegistry()
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
        if _areAABBsOverlapping(aabb, e):
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
    cellRegion = _deepcopy(lattice.cellRegion)


    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))
    cellName = cellRegion.name

    greg = _g4.Registry()
    wlv = _makeWorldVolume(WORLD_DIMENSIONS, "G4_Galactic", greg)


    region_solid = cellRegion.geant4Solid(greg, aabb=None)
    regionLV = _g4.LogicalVolume(region_solid,
                                 "G4_Galactic",
                                 f"{cellName}_lv",
                                 greg)

    lower, upper = regionLV.mesh.getBoundingBox(cellRotation,
                                                cellCentre)
    return _fluka.AABB(lower, upper)

def _isTransformedCellRegionIntersectingWithRegion(region, lattice):
    cellRegion = _deepcopy(lattice.cellRegion)

    transform = lattice.getTransform()

    cellRotation = transform.leftMultiplyRotation(cellRegion.rotation())
    cellCentre = list(transform.leftMultiplyVector(cellRegion.centre()))

    # XXX: Nasty hack to get the cellRegion to return the rotation and
    # centre that I want it to return.  These two lines save me a lot
    # of work elsewhere.
    def rotation(self): return cellRotation
    def centre(self, aabb=None): return cellCentre
    cellRegion.rotation = _types.MethodType(rotation, cellRegion)
    cellRegion.centre = _types.MethodType(centre, cellRegion)

    return _do_intersect(cellRegion.mesh(), region.mesh())

def _checkQuadricRegionAABBs(flukareg, quadricRegionAABBs):
    """Loop over the regions looking for quadrics and for any quadrics we
    find, make sure that that whregion has a defined region aabb in
    quadricRegionAABBs.

    """
    for regionName, region in flukareg.regionDict.items():
        regionBodies = region.bodies()
        quadrics = {r for r in regionBodies if isinstance(r, _fluka.QUA)}

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
    fout = _fluka.FlukaRegistry()
    logger.debug("Filtering half spaces")

    regionAABBs = _regionZoneAABBsToRegionAABBs(regionZoneAABBs)

    for region_name, region in flukareg.regionDict.items():
        regionOut = _deepcopy(region)
        regionAABB = regionAABBs[region_name]
        # Loop over the bodies of this region
        for body in regionOut.bodies():
            # Only potentially omit half spaces
            if isinstance(body, (_fluka.XYP, _fluka.XZP,
                                 _fluka.YZP, _fluka.PLA)):
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
    normal = _fluka.Three(normal).unit()
    return abs(_np.dot(normal, point - pointOnPlane))

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
        cellRotation = list(_trans.reverse(cellRegion.tbxyz()))

        for prototypeName in contents:
            prototypeLV = regionNamesToLVs[prototypeName]
            _g4.PhysicalVolume(cellRotation,
                              cellCentre,
                              prototypeLV,
                              f"{latticeName}_lattice_pv",
                              wlv, greg)

def _makeUniqueQuadricRegions(flukareg, quadricRegionAABBs):
    quadricRegionAABBs = _getMaximalQuadricRegionAABBs(
        flukareg,
        quadricRegionAABBs)

    bodiesToRegions = flukareg.getBodyToRegionsMap()
    flukaRegOut = _fluka.FlukaRegistry()
    for regionName, region in flukareg.regionDict.items():
        if regionName in quadricRegionAABBs:
            uniqueRegion = region.makeUnique("_"+regionName, flukaRegOut)
            flukaRegOut.addRegion(uniqueRegion)
        else:
            newRegion = _deepcopy(region)
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
            if not isinstance(body, _fluka.QUA):
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
        regionAABB = _reduce(_getMaximalOfTwoAABBs,
                             zoneAABBs,
                             zoneAABBs[0])
        regionAABBs[name] = regionAABB
    return regionAABBs


def _copyStructureToNewFlukaRegistry(freg, fregtarget):
    fregtarget.latticeDict = _deepcopy(freg.latticeDict)
    fregtarget.assignmas = _deepcopy(freg.assignmas)
    fregtarget.materials = _deepcopy(freg.materials)
