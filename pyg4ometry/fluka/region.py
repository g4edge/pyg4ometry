import itertools
import logging
from copy import deepcopy
from uuid import uuid4

import networkx as nx

from pyg4ometry.exceptions import FLUKAError, NullMeshError
import pyg4ometry.geant4 as g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix, reverse
from pyg4ometry.fluka.body import Body
from .vector import Three

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


        if isinstance(self.body, Body):
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
    def __init__(self, name=None):
        self.intersections = []
        self.subtractions = []
        self.name = name

    def addSubtraction(self, body):
        self.subtractions.append(Subtraction(body))

    def addIntersection(self,body):
        self.intersections.append(Intersection(body))

    def centre(self, extent=None):
        body_name = self.intersections[0].body.name
        extent = _getExtent(extent, self.intersections[0])
        return self.intersections[0].body.centre(extent=extent)

    def rotation(self):
        return self.intersections[0].body.rotation()

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    def _getSolidFromBoolean(self, boolean, reg, extent):
        try:
            return reg.solidDict[boolean.body.name]
        except KeyError:
            extent = _getExtent(extent, boolean)
            return boolean.body.geant4Solid(reg, extent=extent)

    def geant4Solid(self, reg, extent=None):
        try:
            body0 = self.intersections[0].body
        except IndexError:
            raise FLUKAError("zone has no +")

        result = self._getSolidFromBoolean(self.intersections[0],
                                           reg,
                                           extent)

        booleans = self.intersections + self.subtractions

        for boolean,i in zip(booleans[1:],range(0,len(booleans[1:])+2)):
            boolean_name = boolean.generate_name(i, rootname=self.name)

            tra2 = _get_tra2(body0, boolean.body, extent)
            other_solid = self._getSolidFromBoolean(boolean, reg, extent)
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
        fs = ""

        booleans = self.intersections + self.subtractions
        for s in booleans:
            if isinstance(s,Intersection) :
                if isinstance(s.body,Zone) :
                    fs = fs+" +("+s.body.flukaFreeString()+")"
                else :
                    fs=fs+" +"+s.body.name
            elif isinstance(s,Subtraction) :
                if isinstance(s.body,Zone) :
                    fs = fs+" -("+s.body.flukaFreeString()+")"
                else :
                    fs=fs+" -"+s.body.name
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
        for boolean in self.intersections + self.subtractions:
            body = boolean.body
            name = body.name
            if isinstance(body, Zone):
                body.allBodiesToRegistry(flukaregistry)
            elif name not in flukaregistry.bodyDict:
                flukaregistry.addBody(body)

    def bodies(self):
        bodies = set()
        for boolean in self.intersections + self.subtractions:
            body = boolean.body
            name = body.name
            if isinstance(body, Zone):
                bodies.union(body.bodies())
            else:
                bodies.add(body)
        return bodies

class Region(object):

    def __init__(self, name, material=None):
        self.name = name
        self.zones = []
        self.material = material

    def addZone(self,zone):
        self.zones.append(zone)

    def centre(self, extent=None):
        return self.zones[0].centre(extent=extent)

    def tbxyz(self):
        return self.zones[0].tbxyz()

    def rotation(self):
        return self.zones[0].rotation()

    def bodies(self):
        bodies = set()
        for zone in self.zones:
            bodies = bodies.union(zone.bodies())
        return bodies

    def geant4Solid(self, reg, extent=None):
        logger.debug("Region = %s", self.name)
        try:
            zone0 = self.zones[0]
        except IndexError:
            raise FLUKAError("Region {} has no zones.".format(self.name))

        result = zone0.geant4Solid(reg, extent=extent)
        for zone,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):
            try:
                otherg4 = zone.geant4Solid(reg, extent=extent)
            except FLUKAError as e:
                msg = e.message
                raise FLUKAError("In region {}, {}".format(self.name, msg))
            zone_name = "{}_union_z{}".format(self.name, i)
            tra2 = _get_tra2(zone0, zone, extent=extent)
            logger.debug("union tra2 = %s", tra2)
            result  = g4.solid.Union(zone_name, result, otherg4, tra2, reg)

        return result

    def flukaFreeString(self):
        fs = "region "+self.name

        for z in self.zones :
            fs=fs+" | "+z.flukaFreeString()

        return fs

    def withLengthSafety(self, bigger_flukareg, smaller_flukareg):
        result = Region(self.name)
        for zone in self.zones:
            result.addZone(zone.withLengthSafety(bigger_flukareg,
                                                 smaller_flukareg,
                                                 shrink_intersections=True))
        return result


    def allBodiesToRegistry(self, registry):
        for zone in self.zones:
            zone.allBodiesToRegistry(registry)

    def zoneGraph(self):
        zones = self.zones
        n_zones = len(zones)

        tried = []
        # Build undirected graph, and add nodes corresponding to each zone.
        graph = nx.Graph()
        graph.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(graph)

        # Get extent for each zone
        zone_extents = self._get_zone_extents()

        # Loop over all combinations of zone numbers within this region
        for i, j in itertools.product(range(n_zones), range(n_zones)):
            # Trivially connected to self or tried this combination.
            if i == j or {i, j} in tried:
                continue
            tried.append({i, j})

            # Check if the bounding boxes overlap.  Cheaper than intersecting.
            # if not are_extents_overlapping(zone_extents[i], zone_extents[j]):
            #     continue

            # Check if a path already exists.  Not sure how often this
            # arises but should at least occasionally save some time.
            if nx.has_path(graph, i, j):
                continue

            # Finally: we must do the intersection op.
            logger.debug("Region = %s, int zone %d with %d", self.name, i, j)
            if _get_zone_overlap(zones[i], zones[j], extent=None) is not None:
                graph.add_edge(i, j)
        return graph

    def get_connected_zones(self):
        return list(nx.connected_components(self.zoneGraph()))

    def _get_zone_extents(self):
        material = g4.MaterialPredefined("G4_Galactic")
        extents = []
        for zone in self.zones:
            greg = g4.Registry()
            wlv = _make_wlv(greg)

            zone_solid = zone.geant4Solid(reg=greg)
            lv = g4.LogicalVolume(zone_solid,
                                  material,
                                  _random_name(),
                                  greg)
            rot = list(reverse(list(zone.tbxyz())))
            pv = g4.PhysicalVolume(rot,
                                   list(zone.centre()),
                                   lv,
                                   _random_name(),
                                   wlv, greg)
            lower, upper = wlv.extent()
            extents.append(Extent(lower, upper))
        return extents

    def extent(self):
        greg = g4.Registry()
        world_solid = g4.solid.Box("world_solid", 1e4, 1e4, 1e4, greg, "mm")
        wlv = g4.LogicalVolume(world_solid,
                               g4.MaterialPredefined("G4_Galactic"),
                               "wl", greg)

        region_lv = g4.LogicalVolume(self.geant4Solid(greg),
                                     g4.MaterialPredefined("G4_Galactic"),
                                     "{}_lv".format(self.name),
                                     greg)
        g4.PhysicalVolume(list(reverse(self.tbxyz())),
                          list(self.centre()),
                          region_lv,
                          "{}_pv".format(self.name),
                          wlv, greg)

        lower, upper = wlv.extent()
        return Extent(lower, upper)


def _get_relative_rot_matrix(first, second):
    return first.rotation().T.dot(second.rotation())

def _get_relative_translation(first, second, extent):
    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    extent1 = _getExtent(extent, first)
    extent2 = _getExtent(extent, second)
    offset_vector = second.centre(extent=extent2) - first.centre(extent=extent1)
    mat = first.rotation().T
    offset_vector = mat.dot(offset_vector).view(Three)
    return offset_vector

def _get_relative_rotation(first, second):
    # The first solid is unrotated in a boolean operation, so it
    # is in effect rotated by its inverse.  We apply this same
    # rotation to the second solid to get the correct relative
    # rotation.
    return matrix2tbxyz(_get_relative_rot_matrix(first, second))

def _get_tra2(first, second, extent):
    relative_angles = _get_relative_rotation(first, second)
    relative_translation = _get_relative_translation(first, second, extent)
    relative_transformation = [relative_angles, relative_translation]
    # convert to the tra2 format of a list of lists...

    logger.debug("%s, %s", first.name, second.name)
    logger.debug("relative_angles = %s", relative_angles)
    logger.debug("relative_translation = %s", relative_translation)

    relative_transformation = [list(relative_transformation[0]),
                               list(relative_transformation[1])]
    return relative_transformation

def _random_name():
    return "a{}".format(uuid4()).replace("-", "")

def _make_wlv(reg):
    world_material = g4.MaterialPredefined("G4_Galactic")
    world_solid = g4.solid.Box("world_box", 100, 100, 100, reg, "mm")
    return g4.LogicalVolume(world_solid, world_material, "world_lv", reg)

def are_extents_overlapping(first, second):
    """Check if two Extent instances are overlapping."""
    return not (first.upper.x < second.lower.x
                or first.lower.x > second.upper.x
                or first.upper.y < second.lower.y
                or first.lower.y > second.upper.y
                or first.upper.z < second.lower.z
                or first.lower.z > second.upper.z)

def _get_zone_overlap(zone1, zone2, extent):
    greg = g4.Registry()

    solid1 = zone1.geant4Solid(greg)
    solid2 = zone2.geant4Solid(greg)

    tra2 = _get_tra2(zone1, zone2, extent)

    intersection = g4.solid.Intersection(_random_name(),
                           solid1,
                           solid2,
                           tra2,
                           greg)

    try:
        mesh = intersection.pycsgmesh()
    except NullMeshError:
        return None
    return mesh


class Extent(object):
    def __init__(self, lower, upper):
        self.lower = Three(lower)
        self.upper = Three(upper)
        self.size = self.upper - self.lower
        self.centre = self.upper - 0.5 * self.size

        for i, j in zip(lower, upper):
            if i >= j:
                raise ValueError("Lower extent must be less than upper.")

    def __repr__(self):
        return ("<Extent: Lower({lower.x}, {lower.y}, {lower.z}),"
                " Upper({upper.x}, {upper.y}, {upper.z})>".format(
                    upper=self.upper, lower=self.lower))

    def __eq__(self, other):
        return self.lower == other.lower and self.upper == other.upper

def _getExtent(extent, boolean):
    """Extent can either a dictionary of a number."""
    if isinstance(boolean, Zone):
        return extent
    elif isinstance(boolean, _Boolean):
        body_name = boolean.body.name
    elif isinstance(boolean, Body):
        body_name = boolean.name
    else:
        raise ValueError("Unknown boolean type")

    if extent is None:
        return None
    try:
        return extent[body_name]
    except AttributeError:
        raise
    except KeyError:
        raise KeyError("Failed to find body {} in extent map".format(
            body_name))
