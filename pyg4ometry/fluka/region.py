import itertools
import logging
from copy import deepcopy
from uuid import uuid4
from math import degrees

import networkx as nx

from pyg4ometry.exceptions import FLUKAError, NullMeshError
import pyg4ometry.geant4 as g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix, reverse
from pyg4ometry.fluka.body import BodyMixin
from .vector import Three, Extent, areExtentsOverlapping
from pyg4ometry.transformation import tbxyz2axisangle

import pyg4ometry.config as _config
if _config.meshing == _config.meshingType.pycsg:
    from pyg4ometry.pycsg.core import CSG, do_intersect
    # from pyg4ometry.pycsg.geom import Vector as _Vector
    # from pyg4ometry.pycsg.geom import Vertex as _Vertex
    # from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm:
    from pyg4ometry.pycgal.core import CSG, do_intersect
    # from pyg4ometry.pycgal.geom import Vector as _Vector
    # from pyg4ometry.pycgal.geom import Vertex as _Vertex
    # from pyg4ometry.pycgal.geom import Polygon as _Polygon


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class _Boolean(object):
    def generate_name(self, index, rootname=None):
        """Try to generate a sensible name for intermediate
        Geant4 booleans which have no FLUKA analogue."""
        if rootname is None:
            rootname = "a{}".format(uuid4()).replace("-", "")

        type_name = type(self).__name__
        type_name = type_name[:3]


        if isinstance(self.body, BodyMixin):
            return "{}{}_{}_{}".format(type_name,
                                       index,
                                       self.body.name,
                                       rootname)
        elif isinstance(self.body, Zone):
            return "{}{}_{}_{}".format(type_name,
                                       index,
                                       "zone",
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

class Zone(object):
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

    def centre(self, referenceExtent=None):
        body_name = self.intersections[0].body.name
        referenceExtent = _getReferenceExtent(referenceExtent,
                                              self.intersections[0])
        return self.intersections[0].body.centre(
            referenceExtent=referenceExtent)

    def rotation(self):
        return self.intersections[0].body.rotation()

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    def _getSolidFromBoolean(self, boolean, reg, referenceExtent):
        try:
            return reg.solidDict[boolean.body.name]
        except KeyError:
            referenceExtent = _getReferenceExtent(referenceExtent, boolean)
            return boolean.body.geant4Solid(reg,
                                            referenceExtent=referenceExtent)

    def mesh(self, aabb=None):
        body0 = self.intersections[0].body
        result = body0.mesh(aabb=aabb)
        booleans = self.intersections[1:] + self.subtractions

        for boolean in booleans:
            tra2 = _get_tra2(body0, boolean.body, aabb)
            rot = tbxyz2axisangle(tra2[0])
            tlate = tra2[1]

            mesh = boolean.body.mesh(aabb=aabb)
            mesh.rotate(rot[0], -degrees(rot[1]))
            mesh.translate(tlate)

            if isinstance(boolean, Intersection):
                result = result.intersect(mesh)
            elif isinstance(boolean, Subtraction):
                result = result.subtract(mesh)
        return result

    def geant4Solid(self, reg, referenceExtent=None):
        """Translate this zone to a geant4solid, adding the
        constituent primitive solids and any Booleans to the Geant4
        registry.  Returns the geant4 solid equivalent in geometry to
        this Zone.

        :param reg:  The Registry (geant4) instance to which the
        resulting Geant4 definitions should be added.
        :type reg: Registry
        :param referenceExtent: Optional reference Extent or
        dictionary of body name to Extent instances with which the
        geant4 solid should be evaluated with respect to.  This is the
        entry point to which solid minimisation can be performed.
        :type reg: Extent or dict

        """

        try:
            body0 = self.intersections[0].body
        except IndexError:
            raise FLUKAError("zone has no +.")

        result = self._getSolidFromBoolean(self.intersections[0],
                                           reg,
                                           referenceExtent)

        booleans = self.intersections + self.subtractions

        for boolean,i in zip(booleans[1:],range(0,len(booleans[1:])+2)):
            boolean_name = boolean.generate_name(i, rootname=self.name)

            tra2 = _get_tra2(body0, boolean.body, referenceExtent)
            other_solid = self._getSolidFromBoolean(boolean, reg,
                                                    referenceExtent)
            if isinstance(boolean, Subtraction):
                result = g4.solid.Subtraction(boolean_name,
                                              result, other_solid,
                                              tra2, reg)

            elif isinstance(boolean, Intersection):
                result = g4.solid.Intersection(boolean_name,
                                               result, other_solid,
                                               tra2, reg)
        return result

    def flukaFreeString(self):
        """Returns a string of this Zone innstance in the equivalent
        FLUKA syntax."""
        fs = ""

        booleans = self.intersections + self.subtractions
        for s in booleans:
            if isinstance(s,Intersection) :
                if isinstance(s.body,Zone) :
                    fs += " +({})".format(s.body.flukaFreeString())
                else:
                    fs += " +{}".format(s.body.name)
            elif isinstance(s,Subtraction) :
                if isinstance(s.body,Zone) :
                    fs += " -({})".format(s.body.flukaFreeString())
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


class Region(object):
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

    def centre(self, referenceExtent=None):
        return self.zones[0].centre(referenceExtent=referenceExtent)

    def tbxyz(self):
        return self.zones[0].tbxyz()

    def rotation(self):
        return self.zones[0].rotation()

    def bodies(self):
        "Return the set of unique bodies that constitute this Zone."
        bodies = set()
        for zone in self.zones:
            bodies = bodies.union(zone.bodies())
        return bodies

    def geant4Solid(self, reg, referenceExtent=None):
        logger.debug("Region = %s", self.name)
        try:
            zone0 = self.zones[0]
        except IndexError:
            raise FLUKAError("Region {} has no zones.".format(self.name))

        result = zone0.geant4Solid(reg, referenceExtent=referenceExtent)
        for zone,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):
            try:
                otherg4 = zone.geant4Solid(reg, referenceExtent=referenceExtent)
            except FLUKAError as e:
                msg = e.message
                raise FLUKAError("In region {}, {}".format(self.name, msg))
            zone_name = "{}_union_z{}".format(self.name, i)
            tra2 = _get_tra2(zone0, zone, referenceExtent=referenceExtent)
            logger.debug("union tra2 = %s", tra2)
            result  = g4.solid.Union(zone_name, result, otherg4, tra2, reg)

        return result

    def flukaFreeString(self):
        #fs = "region "+self.name
        fs = self.name+" "+str(5)

        for z in self.zones :
            fs=fs+" | "+z.flukaFreeString()

        if self.comment != "" :
            fs = "* "+self.comment+"\n"+fs

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

    def zoneGraph(self, zoneExtents=None, referenceExtent=None):
        zones = self.zones
        n_zones = len(zones)

        tried = []
        # Build undirected graph, and add nodes corresponding to each zone.
        graph = nx.Graph()
        graph.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(graph)

        # We allow the user to provide a list of zoneExtents as an
        # optimisation, but if they have not been provided, then we
        # will generate them here
        if zoneExtents is None:
            zoneExtents = self.zoneExtents(
                referenceExtent=referenceExtent)

        # Loop over all combinations of zone numbers within this region
        for i, j in itertools.product(range(n_zones), range(n_zones)):
            # Trivially connected to self or tried this combination.
            if i == j or {i, j} in tried:
                continue
            tried.append({i, j})

            # Check if the bounding boxes overlap.  Cheaper than intersecting.
            if not areExtentsOverlapping(zoneExtents[i], zoneExtents[j]):
                continue

            # Check if a path already exists.  Not sure how often this
            # arises but should at least occasionally save some time.
            if nx.has_path(graph, i, j):
                continue

            # Finally: we must do the intersection op.
            logger.debug("Region = %s, int zone %d with %d", self.name, i, j)
            if areOverlapping(zones[i], zones[j],
                              referenceExtent=referenceExtent):
                graph.add_edge(i, j)
        return graph

    def connectedZones(self, zoneExtents=None, referenceExtent=None):
        return list(nx.connected_components(
            self.zoneGraph(zoneExtents=zoneExtents,
                referenceExtent=referenceExtent)))

    def zoneExtents(self, referenceExtent=None):
        material = g4.MaterialPredefined("G4_Galactic")
        extents = []
        for zone in self.zones:
            greg = g4.Registry()
            wlv = _make_wlv(greg)

            try:
                zone_solid = zone.geant4Solid(reg=greg,
                                              referenceExtent=referenceExtent)
            except FLUKAError as e:
                raise FLUKAError("Error in region {}: {}".format(self.name,
                                                                 e.message))

            try:
                zoneLV = g4.LogicalVolume(zone_solid,
                                          material,
                                          _random_name(),
                                          greg)
            except NullMeshError as e:
                raise NullMeshError("Null zone in region {}: {}.".format(
                    self.name,
                    e.message))

            lower, upper = zoneLV.mesh.getBoundingBox(zone.rotation(),
                                                      zone.centre())

            extents.append(Extent(lower, upper))
        return extents

    def extent(self, referenceExtent=None):
        greg = g4.Registry()
        world_solid = g4.solid.Box("world_solid", 1e4, 1e4, 1e4, greg, "mm")
        wlv = g4.LogicalVolume(world_solid,
                               g4.MaterialPredefined("G4_Galactic"),
                               "wl", greg)
        solid = self.geant4Solid(greg, referenceExtent=referenceExtent)
        regionLV = g4.LogicalVolume(solid,
                                    g4.MaterialPredefined("G4_Galactic"),
                                    "{}_lv".format(self.name),
                                    greg)

        lower, upper = regionLV.mesh.getBoundingBox(
            self.rotation(),
            self.centre(referenceExtent=referenceExtent))

        return Extent(lower, upper)

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

def _get_relative_rot_matrix(first, second):
    return first.rotation().T.dot(second.rotation())

def _get_relative_translation(first, second, referenceExtent):
    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    referenceExtent1 = _getReferenceExtent(referenceExtent, first)
    referenceExtent2 = _getReferenceExtent(referenceExtent, second)
    offset_vector = (second.centre(referenceExtent=referenceExtent2)
                     - first.centre(referenceExtent=referenceExtent1))
    mat = first.rotation().T
    offset_vector = mat.dot(offset_vector).view(Three)
    return offset_vector

def _get_relative_rotation(first, second):
    # The first solid is unrotated in a boolean operation, so it
    # is in effect rotated by its inverse.  We apply this same
    # rotation to the second solid to get the correct relative
    # rotation.
    return matrix2tbxyz(_get_relative_rot_matrix(first, second))

def _get_tra2(first, second, referenceExtent):
    relative_angles = _get_relative_rotation(first, second)
    relative_translation = _get_relative_translation(first, second,
                                                     referenceExtent)
    relative_transformation = [relative_angles, relative_translation]
    # convert to the tra2 format of a list of lists...

    logger.debug("%s, %s", first.name, second.name)
    logger.debug("relative_angles = %s", relative_angles)
    logger.debug("relative_translation = %s", relative_translation)

    relative_transformation = [list(relative_transformation[0]),
                               list(relative_transformation[1])]
    return relative_transformation

def _random_name():
    "Returns a random name that is syntactically correct for use in GDML."
    return "a{}".format(uuid4()).replace("-", "")

def _make_wlv(reg):
    world_material = g4.MaterialPredefined("G4_Galactic")
    world_solid = g4.solid.Box("world_box", 100, 100, 100, reg, "mm")
    return g4.LogicalVolume(world_solid, world_material, "world_lv", reg)

def areOverlapping(first, second, referenceExtent=None):
    """Determine if two Region, Zone, or Body instances are
    overlapping, with the option to provide a reference Extent with
    which the two operands may be evaluated with respect to.

    :param first: The first Body, Zone, or Region instance with which
    we check for overlaps with the second.
    :type first: Body or Zone or Region
    :param second: The second Body, Zone, or Region instance with which
    we check for overlaps with the first.
    :type second: Body or Zone or Region
    :param referenceExtent: An Extent or dictionary of Extent
    instances with which the two operands should be evaluated with
    respect to.
    :type referenceExtent: Extent or dict

    """
    greg = g4.Registry()

    solid1 = first.geant4Solid(greg, referenceExtent=referenceExtent)
    solid2 = second.geant4Solid(greg, referenceExtent=referenceExtent)

    tbxyz, tra = _get_tra2(first, second, referenceExtent)
    rot = tbxyz2axisangle(tbxyz)

    mesh1 = solid1.mesh()
    mesh2 = solid2.mesh()

    mesh2.rotate(rot[0], -degrees(rot[1]))
    mesh2.translate(tra)
    return do_intersect(mesh1, mesh2)

def _getReferenceExtent(referenceExtent, boolean):
    """referenceExtent should really be a dictionary of
    {bodyName: extentInstance}."""
    if isinstance(boolean, (Zone, Region)):
        return referenceExtent
    elif isinstance(boolean, _Boolean):
        body_name = boolean.body.name
    elif isinstance(boolean, BodyMixin):
        body_name = boolean.name
    else:
        raise ValueError("Unknown boolean type")

    if body_name is None:
        return referenceExtent

    if (isinstance(boolean, (Subtraction, Intersection))
            and isinstance(boolean.body, Zone)):
        return referenceExtent

    if referenceExtent is None:
        return None
    try:
        return referenceExtent[body_name]
    except AttributeError:
        raise
    except KeyError:
        # This can happen if we have provided a referenceExtentMap for
        # the Quadrics but have not yet generated extents for the
        # other bodies.
        logger.debug("%s not found in %s", body_name, referenceExtent)
        return None
