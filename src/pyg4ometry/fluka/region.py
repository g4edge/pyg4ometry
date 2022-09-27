import itertools
import logging
from copy import deepcopy
from uuid import uuid4
from math import degrees

import numpy as np
import networkx as nx

from . import vis
from pyg4ometry.exceptions import FLUKAError, NullMeshError
import pyg4ometry.geant4 as g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix, reverse
from pyg4ometry.fluka.body import BodyMixin
from .vector import Three, AABB, areAABBsOverlapping
from . import boolean_algebra
from pyg4ometry.transformation import tbxyz2axisangle

import pyg4ometry.config as _config
if _config.meshing == _config.meshingType.pycsg:
    from pyg4ometry.pycsg.core import CSG, do_intersect
elif _config.meshing == _config.meshingType.cgal_sm:
    pass
    # TODO reinstate intersecting meshes
    #from pyg4ometry.pycgal.core import CSG, do_intersect, intersecting_meshes

from textwrap import wrap as _wrap

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



def _generate_name(typename,index, name, isZone, rootname):
    """Try to generate a sensible name for intermediate
    Geant4 booleans which have no FLUKA analogue."""
    if rootname is None:
        rootname = "a{}".format(uuid4()).replace("-", "")


    if isZone:
        return "{}{}_{}_{}".format(typename,
                                   index,
                                   "zone",
                                   rootname)
    else:
        return "{}{}_{}_{}".format(typename,
                                   index,
                                   name,
                                   rootname)


class _Boolean(object):
    def generate_name(self, index, rootname=None):
        typename = type(self).__name__
        typename = typename[:3]
        return _generate_name(typename,
                              index,
                              self.body.name,
                              isinstance(self.body, Zone),
                              rootname)

class Subtraction(_Boolean):
    def __init__(self, body):
        self.body = body
        self._typestring = "sub"

class Intersection(_Boolean):
    def __init__(self, body):
        self.body = body
        self._typestrin = "int"

class Union(_Boolean):
    def __init__(self, body):
        self.body = body
        self._typestring = "uni"

class Zone(vis.ViewableMixin):
    """Represents a zone which consists of one or more body intersections
    and zero or more body subtractions.  May also be used to represent
    subzones, which are zones nested within zones, for example the form
    +A -B -(+C -D).  Once instantiated, intersections and subtractions
    can be added to this instance with the addIntersection and
    addSubtraction method.

    :param name: Optional name for the zone.  This is used to provide
    more informative names in any resulting geant4solid.
    :type name: string

    """
    def __init__(self, name=None):
        self.intersections = []
        self.subtractions = []
        self.name = name

    def addSubtraction(self, body):
        """Add a body or subzone as a subtraction to this Zone
        instance.

        :param body: Body or Zone instance.
        :type body: Body or Zone
        """
        self.subtractions.append(Subtraction(body))

    def addIntersection(self,body):
        """Add a body or subzone as an intersection to this Zone
        instance.

        :param body: Body or Zone instance.
        :type: body: Body or Zone
        """
        self.intersections.append(Intersection(body))

    def centre(self, aabb=None):
        body_name = self.intersections[0].body.name
        aabb = _getAxisAlignedBoundingBox(aabb, self.intersections[0])
        return self.intersections[0].body.centre(aabb=aabb)

    def rotation(self):
        return self.intersections[0].body.rotation()

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    @staticmethod
    def _getSolidFromBoolean(boolean, g4reg, aabb):
        # For given _Boolean instance, get the underlying fluka.Body
        # instance as a GDML solid.  Either it has already been defined and
        # get it from the Geant4 Registry or define it here w.r.t the
        # provdided AABB and add it to the geant4 registry provided.
        try:
            return g4reg.solidDict[boolean.body.name]
        except KeyError:
            aabb = _getAxisAlignedBoundingBox(aabb, boolean)
            return boolean.body.geant4Solid(g4reg, aabb=aabb)

    def mesh(self, aabb=None):
        result = self.intersections[0].body.mesh(aabb=aabb)
        for boolean in self.intersections[1:] + self.subtractions:
            mesh = boolean.body.mesh(aabb=aabb)

            if isinstance(boolean, Intersection):
                result = result.intersect(mesh)
            elif isinstance(boolean, Subtraction):
                result = result.subtract(mesh)
        return result

    def geant4Solid(self, reg, aabb=None):
        """Translate this zone to a geant4solid, adding the
        constituent primitive solids and any Booleans to the Geant4
        registry.  Returns the geant4 solid equivalent in geometry to
        this Zone.

        :param reg:  The Registry (geant4) instance to which the
        resulting Geant4 definitions should be added.
        :type reg: Registry
        :param aabb: Optional reference AABB or
        dictionary of body name to AABB instances with which the
        geant4 solid should be evaluated with respect to.  This is the
        entry point to which solid minimisation can be performed.
        :type reg: AABB or dict

        """

        try:
            body0 = self.intersections[0].body
        except IndexError:
            raise FLUKAError("zone has no +.")

        result = self._getSolidFromBoolean(self.intersections[0], reg, aabb)
        result = self._combine_booleans(body0,
                                        result,
                                        self.intersections[1:],
                                        g4.solid.Intersection,
                                        reg,
                                        aabb)

        if not self.subtractions:
            return result
        elif len(self.subtractions) < 5:
            return self._combine_booleans(body0,
                                          result,
                                          self.subtractions,
                                          g4.solid.Subtraction,
                                          reg,
                                          aabb)
        else:
            return self._geant4MultiUnionSubtraction(body0, result, reg, aabb)

    def _combine_booleans(self, body0, start, collection, operation, reg, aabb):
        result = start
        for i, boolean in enumerate(collection):
            boolean_name = boolean.generate_name(i, rootname=self.name)
            transform = _getRelativeTransform(body0, boolean.body, aabb)
            other_solid = self._getSolidFromBoolean(boolean, reg, aabb)
            result = operation(boolean_name,
                               result, other_solid,
                               transform, reg)
        return result

    def _geant4MultiUnionSubtraction(self, body0, start, reg, aabb):
        solids = []
        transforms = []
        for sub in self.subtractions:
            body = sub.body
            solids.append(self._getSolidFromBoolean(sub, reg, aabb))
            thisAABB = _getAxisAlignedBoundingBox(aabb, sub)
            transforms.append([body.tbxyz(), list(body.centre(aabb=thisAABB))])

        union = g4.solid.MultiUnion(f"{self.name}_munion_{_randomName()}",
                                    solids,
                                    transforms,
                                    registry=reg)
        aabb0 = _getAxisAlignedBoundingBox(aabb, body0)

        # Getting the correct relative rotation for the subtraction.
        rotation = body0.rotation().T
        translation = -1 * body0.centre(aabb=aabb0)
        translation = list(rotation.dot(translation))
        rotation = list(matrix2tbxyz(rotation))
        result = g4.solid.Subtraction(f"{self.name}_msub_{_randomName()}",
                                      start, union,
                                      [rotation, translation], reg)
        return result

    def dumps(self):
        """Returns a string of this Zone instance in the equivalent
        FLUKA syntax."""
        fs = ""

        booleans = self.intersections + self.subtractions
        for s in booleans:
            if isinstance(s,Intersection) :
                if isinstance(s.body,Zone) :
                    fs += " +({})".format(s.body.dumps())
                else:
                    fs += " +{}".format(s.body.name)
            elif isinstance(s,Subtraction) :
                if isinstance(s.body,Zone) :
                    fs += " -({})".format(s.body.dumps())
                else :
                    fs += " -{}".format(s.body.name)

        return fs

    def withLengthSafety(self, bigger_flukareg, smaller_flukareg,
                           shrink_intersections):
        zone_out = Zone(name=self.name)
        logger.debug("zone.name = %s", self.name)
        for boolean in self.intersections:
            body = boolean.body
            name = body.name

            if isinstance(body, Zone):
                zone_out.addIntersection(body.withLengthSafety(
                    bigger_flukareg,
                    smaller_flukareg,
                    shrink_intersections))
            elif shrink_intersections:
                ls_body = deepcopy(smaller_flukareg.getBody(name))
                ls_body.name += "_s"
                logger.debug("Adding shrunk intersection %s to registry",
                             ls_body.name)
                zone_out.addIntersection(ls_body)
            else:
                ls_body = deepcopy(bigger_flukareg.getBody(name))
                ls_body.name += "_e"
                logger.debug("Adding expanded intersection %s to registry",
                             ls_body.name)
                zone_out.addIntersection(ls_body)

        for boolean in self.subtractions:
            body = boolean.body
            name = body.name
            if isinstance(body, Zone):
                zone_out.addSubtraction(body.withLengthSafety(
                    bigger_flukareg,
                    smaller_flukareg,
                    not shrink_intersections)) # flip length safety
                # convention if entering a subtracted subzone.
            elif shrink_intersections:
                ls_body = deepcopy(bigger_flukareg.getBody(name))
                ls_body.name += "_e"
                logger.debug("Adding expanded subtraction %s to registry",
                             ls_body.name)
                zone_out.addSubtraction(ls_body)
            else:
                ls_body = deepcopy(smaller_flukareg.getBody(name))
                ls_body.name += "_s"
                logger.debug("Adding shrunk subtraction %s to registry",
                             ls_body.name)
                zone_out.addSubtraction(ls_body)
        return zone_out

    def allBodiesToRegistry(self, flukaregistry):
        """Add all the bodies that contitute this Zone to the provided
        FlukaRegistry instance.

        :param flukaregistry: FlukaRegistry instance to which
        constituent bodies will be added.
        :type flukaregistry: FlukaRegistry

        """
        for boolean in self.intersections + self.subtractions:
            body = boolean.body
            name = body.name
            if isinstance(body, Zone):
                body.allBodiesToRegistry(flukaregistry)
            elif name not in flukaregistry.bodyDict:
                flukaregistry.addBody(body)

    def bodies(self):
        "Return the set of unique bodies that constitute this Zone."
        bodies = set()
        for boolean in self.intersections + self.subtractions:
            body = boolean.body
            name = body.name
            if isinstance(body, Zone):
                bodies = bodies.union(body.bodies())
            else:
                bodies.add(body)
        return bodies

    def removeBody(self, name):
        """Remove a body from this zone by name.

        :param name: The name of the body to be removed.
        :type name: string

        """
        newIntersections = []
        for intsx in self.intersections:
            if isinstance(intsx, Zone):
                intsx.body.removeBody(name)
                newIntersections.append(intsx)
            elif intsx.body.name != name:
                newIntersections.append(intsx)

        newSubtractions = []
        for subt in self.subtractions:
            if isinstance(subt, Zone):
                subt.body.removeBody(name)
                newSubtractions.append(subt)
            elif subt.body.name != name:
                newSubtractions.append(subt)

        self.intersections = newIntersections
        self.subtractions = newSubtractions

    def makeUnique(self, nameSuffix, flukaregistry):
        """Get this zone with every constituent body recreated with a
        unique name by appending nameSuffix.

        :param nameSuffix: The string to append to the names of the
        bodies.
        :param flukaregistry: the FlukaRegisytr instance to add the
        uniquely defined bodies to.
        """

        result = Zone()
        nestedZoneCount = 0
        for boolean in self.intersections + self.subtractions:
            body = boolean.body
            if body.name is None: # e.g. a zone with no name
                name = "zone{}_{}".format(nestedZoneCount, nameSuffix)
                nestedZoneCount += 1
            else:
                name = body.name + nameSuffix

            booleanType = type(boolean)

            if isinstance(body, Zone):
                if booleanType is Intersection:
                    result.addIntersection(body.makeUnique(
                        flukaregistry=flukaregistry,
                        nameSuffix=nameSuffix))
                elif booleanType is Subtraction:
                    result.addSubtraction(body.makeUnique(
                        flukaregistry=flukaregistry,
                        nameSuffix=nameSuffix))
            else:
                if name in flukaregistry.bodyDict:
                    newBody = flukaregistry.getBody(name)
                else:
                    newBody = deepcopy(body)
                    newBody.name = name
                    flukaregistry.addBody(newBody)

                if booleanType is Intersection:
                    result.addIntersection(newBody)
                elif booleanType is Subtraction:
                    result.addSubtraction(newBody)
                else:
                    raise ValueError("Unknown Boolean type")
        return result

    def isNull(self, aabb=None):
        return self.mesh(aabb=aabb).isNull()

    def toDNF(self, name):
        r = Region(name)
        r.zones = boolean_algebra.zoneToDNFZones(self)
        return r

    def isDNF(self):
        parts = self.intersections + self.subtractions
        return not any(isinstance(b.body, Zone) for b in parts)

    def leafCount(self):
        total = 0
        for body in self.intersections + self.subtractions:
            b = body.body
            if isinstance(b, Zone):
                total += b.leafCount()
            else:
                total += 1
        return total


class Region(vis.ViewableMixin):
    """Represents a region which consists of a region name, one or more
    zones, and a single material.  Metadata may be provided with the
    comment kwarg, which is used when writing to FLUKA to provide
    contextual information to the physicist.

    :param name: The name of this region.
    :type name: str
    :param material: The name of a material.
    :type material: str
    :param comment: Optional descriptive comment.
    :type param: str

    """

    def __init__(self, name, comment = ""):
        self.name = name
        self.zones = []
        self.comment = comment

    def addZone(self,zone):
        """Add a Zone instance to this region.

        :param zone: The Zone instance to be added.
        :type zone: Zone

        """
        self.zones.append(zone)

    def centre(self, aabb=None):
        if len(self.zones) == 1:
            return self.zones[0].centre(aabb=aabb)
        else:
            return [0, 0, 0] # Multi union origin is [0, 0, 0].

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    def rotation(self):
        if len(self.zones) == 1:
            return self.zones[0].rotation()
        else:
            return np.identity(3) # Multi union is already rotated.

    def bodies(self):
        "Return the set of unique bodies that constitute this Zone."
        bodies = set()
        for zone in self.zones:
            bodies = bodies.union(zone.bodies())
        return bodies

    def mesh(self, aabb=None):
        result = self.zones[0].mesh(aabb=aabb)
        for zone in self.zones[1:]:
            mesh = zone.mesh(aabb=aabb)
            result = result.union(mesh)
        return result

    def geant4Solid(self, reg, aabb=None):
        """Get the geant4Solid instance corresponding to this Region."""
        if len(self.zones) == 0:
            raise FLUKAError("Region {} has no zones.".format(self.name))
        elif len(self.zones) == 1:
            return self.zones[0].geant4Solid(reg, aabb=aabb)
        # Do multi-unions for everything else to support possible disjointedness.
        solids = []
        transforms = []
        for zone in self.zones:
            solids.append(zone.geant4Solid(reg, aabb=aabb))
            transforms.append([zone.tbxyz(), list(zone.centre(aabb=aabb))])

        return g4.solid.MultiUnion(f"{self.name}_solid",
                                   solids,
                                   transforms,
                                   registry=reg)

    def dumps(self):
        return "\n".join([f"|{z.dumps()}" for z in self.zones])

    def flukaFreeString(self):
        fs = f"{self.name} 5 {self.dumps()}"

        # split line (132 characters)
        linLen = 132-5
        barPos = fs.find("|")
        modLen = linLen-barPos

        fsLines = _wrap(fs,modLen)

        fsNew = fsLines[0]+"\n"
        for l in fsLines[1:] :
            fsNew = fsNew + barPos*" " + l + "\n"

        fs = fsNew
        if self.comment:
            fs = f"* {self.comment}\n{fs}"
        return fs

    def withLengthSafety(self, bigger_flukareg, smaller_flukareg):
        result = Region(self.name)
        for zone in self.zones:
            result.addZone(zone.withLengthSafety(bigger_flukareg,
                                                 smaller_flukareg,
                                                 shrink_intersections=True))
        return result


    def allBodiesToRegistry(self, registry):
        """Add all the bodies that constitute this Region to the provided
        FlukaRegistry instance.

        :param flukaregistry: FlukaRegistry instance to which
        constituent bodies will be added.
        :type flukaregistry: FlukaRegistry

        """
        for zone in self.zones:
            zone.allBodiesToRegistry(registry)

    def zoneGraph(self, zoneAABBs=None, aabb=None):
        if _config.meshing == _config.meshingType.cgal_sm:
            return self._zoneGraphPycgal()

        zones = self.zones
        n_zones = len(zones)

        tried = []
        # Build undirected graph, and add nodes corresponding to each zone.
        graph = nx.Graph()
        graph.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(graph)

        # We allow the user to provide a list of zoneAABBs as an
        # optimisation, but if they have not been provided, then we
        # will generate them here
        if zoneAABBs is None:
            zoneAABBs = self.zoneAABBs(aabb=aabb)

        # Loop over all combinations of zone numbers within this region
        for i, j in itertools.product(range(n_zones), range(n_zones)):
            # Trivially connected to self or tried this combination.
            if i == j or {i, j} in tried:
                continue
            tried.append({i, j})

            # Check if the bounding boxes overlap.  Cheaper than intersecting.
            if not areAABBsOverlapping(zoneAABBs[i], zoneAABBs[j]):
                continue

            # Check if a path already exists.  Not sure how often this
            # arises but should at least occasionally save some time.
            if nx.has_path(graph, i, j):
                graph.add_edge(i, j)
                continue

            # Finally: we must do the intersection op.
            logger.debug("Region = %s, int zone %d with %d", self.name, i, j)
            if do_intersect(zones[i].mesh(aabb=aabb), zones[j].mesh(aabb=aabb)):
                graph.add_edge(i, j)

        return graph

    def _zoneGraphPycgal(self):
        meshes = [z.mesh() for z in self.zones]
        intersections = intersecting_meshes(meshes)
        graph = nx.Graph()
        graph.add_nodes_from(range(len(self.zones)))
        graph.add_edges_from(intersections)
        return graph

    def connectedZones(self, zoneAABBs=None, aabb=None):
        return list(nx.connected_components(
            self.zoneGraph(zoneAABBs=zoneAABBs, aabb=aabb)))

    def zoneAABBs(self, aabb=None):
        extents = []
        for zone in self.zones:
            try:
                zoneExtent = AABB.fromMesh(zone.mesh(aabb=aabb))
            except ValueError:
                zoneExtent = None
            extents.append(zoneExtent)

        return extents

    def aabb(self, aabb=None):
        return AABB.fromMesh(self.mesh(aabb=aabb))

    def removeBody(self, name):
        """Remove a body from this region by name.

        :param name: The name of the body to be removed.
        :type name: string

        """
        for zone in self.zones:
            zone.removeBody(name)

    def makeUnique(self, nameSuffix, flukaregistry):
        """Get this Region instance with every constituent body
        with a unique name by appending nameSuffix to each Body
        instance.

        :param nameSuffix: string to append to each Body instance.
        :param flukaregistry: FlukaRegisty instance to add each
        newly-defined body to."""

        result = Region(self.name)
        for zone in self.zones:
            result.addZone(zone.makeUnique(flukaregistry=flukaregistry,
                                           nameSuffix=nameSuffix))
        return result

    def isNull(self, aabb=None):
        return all(z.isNull(aabb=aabb) for z in self.zones)

    def toDNF(self, name):
        result = Region(name)
        for zone in self.zones:
            if zone.isDNF():
                result.zones.append(zone)
            else:
                result.zones.extend(boolean_algebra.zoneToDNFZones(zone))
        return result

    def isDNF(self):
        return all(z.isDNF() for z in self.zones)

    def filterNullZones(self, aabb=None):
        self.zones = [z for z in self.zones if not z.isNull(aabb=aabb)]

    def leafCount(self):
        return sum(z.leafCount() for z in self.zones)

    def simplify(self):
        reg = boolean_algebra.pruneRegion(self)
        if not reg.zones:
            raise NullMeshError(f"Pruned region {self.name} is null.")
        boolean_algebra.simplifyRegion(reg)
        self.zones = reg.zones

    def __repr__(self):
        return f"<Region: {self.name}>"

    def removeZones(self, indices):
        """Remove zones by index"""
        for index in reversed(sorted(indices)):
            # print(self.zones)
            # print(index)
            del self.zones[index]


def _get_relative_rot_matrix(first, second):
    return first.rotation().T.dot(second.rotation())

def _get_relative_translation(first, second, aabb):
    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    aabb1 = _getAxisAlignedBoundingBox(aabb, first)
    aabb2 = _getAxisAlignedBoundingBox(aabb, second)
    offset_vector = (second.centre(aabb=aabb2) - first.centre(aabb=aabb1))
    mat = first.rotation().T
    offset_vector = mat.dot(offset_vector).view(Three)
    return offset_vector

def _get_relative_rotation(first, second):
    # The first solid is unrotated in a boolean operation, so it
    # is in effect rotated by its inverse.  We apply this same
    # rotation to the second solid to get the correct relative
    # rotation.
    return matrix2tbxyz(_get_relative_rot_matrix(first, second))

def _getRelativeTransform(first, second, aabb):
    relative_angles = _get_relative_rotation(first, second)
    relative_translation = _get_relative_translation(first, second,
                                                     aabb)
    relative_transformation = [relative_angles, relative_translation]
    # convert to the tra2 format of a list of lists...

    logger.debug("%s, %s", first.name, second.name)
    logger.debug("relative_angles = %s", relative_angles)
    logger.debug("relative_translation = %s", relative_translation)

    relative_transformation = [list(relative_transformation[0]),
                               list(relative_transformation[1])]
    return relative_transformation

def _randomName():
    "Returns a random name that is syntactically correct for use in GDML."
    return "a{}".format(uuid4()).replace("-", "")

def _makeWorldLogicalVolume(reg):
    world_material = g4.MaterialPredefined("G4_Galactic")
    world_solid = g4.solid.Box("world_box", 100, 100, 100, reg, "mm")
    return g4.LogicalVolume(world_solid, world_material, "world_lv", reg)

def _getAxisAlignedBoundingBox(aabb, boolean):
    """aabb should really be a dictionary of
    {bodyName: extentInstance}."""
    if isinstance(boolean, (Zone, Region)):
        return aabb
    elif isinstance(boolean, _Boolean):
        body_name = boolean.body.name
    elif isinstance(boolean, BodyMixin):
        body_name = boolean.name
    else:
        raise ValueError("Unknown boolean type")

    if body_name is None:
        return aabb

    if (isinstance(boolean, (Subtraction, Intersection))
            and isinstance(boolean.body, Zone)):
        return aabb

    if aabb is None:
        return None
    try:
        return aabb[body_name]
    except AttributeError:
        raise
    except KeyError:
        # This can happen if we have provided a aabbMap for
        # the Quadrics but have not yet generated extents for the
        # other bodies.
        logger.debug("%s not found in %s", body_name, aabb)
        return None
