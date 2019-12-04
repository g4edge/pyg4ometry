import itertools
import logging
from copy import deepcopy
from uuid import uuid4

import networkx as nx

from pyg4ometry.exceptions import FLUKAError, NullMeshError
import pyg4ometry.geant4 as _g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix
from pyg4ometry.fluka.Body import Body as _Body
from .Vector import Three


# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


class _Boolean(object):
    def generate_name(self, index, rootname=None):
        """Try to generate a sensible name for intermediate
        Geant4 booleans which have no FLUKA analogue."""
        if rootname is None:
            rootname = "a{}".format(uuid4()).replace("-", "")

        type_name = type(self).__name__
        type_name = type_name[:3]


        if isinstance(self.body, _Body):
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

    def centre(self):
        return self.intersections[0].body.centre()

    def rotation(self):
        return self.intersections[0].body.rotation()

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    def _getSolidFromBoolean(self, boolean, reg):
        try:
            return reg.solidDict[boolean.body.name]
        except KeyError:
            return boolean.body.geant4_solid(reg)

    def geant4_solid(self, reg):
        try:
            body0 = self.intersections[0].body
        except IndexError:
            raise FLUKAError("Each zone must consist of at least one +.")

        result = self._getSolidFromBoolean(self.intersections[0], reg)

        booleans = self.intersections + self.subtractions

        for boolean,i in zip(booleans[1:],range(0,len(booleans[1:])+2)):
            boolean_name = boolean.generate_name(i, rootname=self.name)
            print i, boolean_name

            tra2 = _get_tra2(body0, boolean.body)
            logger.debug("subint tra2 = %s", tra2)
            other_solid = self._getSolidFromBoolean(boolean, reg)
            if isinstance(boolean, Subtraction):
                result  =_g4.solid.Subtraction(boolean_name,
                                               result, other_solid,
                                               tra2, reg)

            elif isinstance(boolean, Intersection):
                result  =_g4.solid.Intersection(boolean_name,
                                                result, other_solid,
                                                tra2, reg)
        return result

    def fluka_free_string(self):
        fs = ""

        booleans = self.intersections + self.subtractions
        for s in booleans:
            if isinstance(s,Intersection) :
                if isinstance(s.body,Zone) :
                    fs = fs+" +("+s.body.fluka_free_string()+")"
                else :
                    fs=fs+" +"+s.body.name
            elif isinstance(s,Subtraction) :
                if isinstance(s.body,Zone) :
                    fs = fs+" -("+s.body.fluka_free_string()+")"
                else :
                    fs=fs+" -"+s.body.name
        return fs

    def with_length_safety(self, bigger_flukareg, smaller_flukareg,
                           shrink_intersections):
        zone_out = Zone(name=self.name)
        logger.debug("zone.name = %s", self.name)
        for boolean in self.intersections:
            body = boolean.body
            name = body.name

            if isinstance(body, Zone):
                zone_out.addIntersection(body.with_length_safety(
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
                zone_out.addSubtraction(body.with_length_safety(
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



class Region(object):

    def __init__(self, name, material=None):
        self.name = name
        self.zones = []
        self.material = material

    def addZone(self,zone):
        self.zones.append(zone)

    def centre(self):
        return self.zones[0].centre()

    def tbxyz(self):
        return self.zones[0].tbxyz()

    def rotation(self):
        return self.zones[0].rotation()

    def geant4_solid(self, reg):
        try:
            zone0 = self.zones[0]
        except IndexError:
            raise FLUKAError("Region {} has no zones.".format(self.name))

        result = zone0.geant4_solid(reg)
        for zone,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):
            other_g4 = zone.geant4_solid(reg)
            zone_name = "{}_union_z{}".format(self.name, i)
            print i, zone_name
            tra2 = _get_tra2(zone0, zone)
            logger.debug("union tra2 = %s", tra2)
            result  = _g4.solid.Union(zone_name, result, other_g4, tra2, reg)

        return result

    def geant4_test(self):
        reg = _g4.Registry()
        wb  = _g4.solid.Box("world_solid",50,50,50,reg,"mm")
        wl  = _g4.LogicalVolume(wb,"G4_Galactic","world_logical",reg,True)
        fs  = self.geant4_solid(reg)
        fl  = _g4.LogicalVolume(fs,"G4_Fe","fluka_solid",reg,True)
        fp  = _g4.PhysicalVolume([0,0,0],[0,0,0],fl,"fluka_placement",wl,reg)

        return wl


    def fluka_free_string(self):
        fs = "region "+self.name

        for z in self.zones :
            fs=fs+" | "+z.fluka_free_string()

        return fs

    def with_length_safety(self, bigger_flukareg, smaller_flukareg):
        result = Region(self.name)
        for zone in self.zones:
            result.addZone(zone.with_length_safety(bigger_flukareg,
                                                   smaller_flukareg,
                                                   shrink_intersections=True))
        return result


    def allBodiesToRegistry(self, registry):
        for zone in self.zones:
            zone.allBodiesToRegistry(registry)

    def get_connected_zones(self):
        zones = self.zones
        n_zones = len(zones)

        tried = []
        # Build undirected graph, and add nodes corresponding to each zone.
        graph = nx.Graph()
        graph.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(graph)
        # Build up a cache of booleans and extents for each zone.
        # format: {zone_index: (boolean, extent)}

        zone_extents = self._get_zone_extents()

        # Loop over all combinations of zone numbers within this region
        for i, j in itertools.product(range(n_zones), range(n_zones)):
            # Trivially connected to self or tried this combination.
            if i == j or {i, j} in tried:
                continue
            tried.append({i, j})

            # Check if the bounding boxes overlap.  Cheaper than intersecting.
            if not are_extents_overlapping(zone_extents[i], zone_extents[j]):
                continue

            # Check if a path already exists.  Not sure how often this
            # arises but should at least occasionally save some time.
            if nx.has_path(graph, i, j):
                continue

            # Finally: we must do the intersection op.
            logger.debug("Intersecting zone %d with %d", i, j)
            if _get_zone_overlap(zones[i], zones[j]) is not None:
                graph.add_edge(i, j)
        return list(nx.connected_components(graph))

    def _get_zone_extents(self):
        material = _g4.MaterialPredefined("G4_Galactic")
        extents = []
        for zone in self.zones:
            greg = _g4.Registry()
            wlv = _make_wlv(greg)

            zone_solid = zone.geant4_solid(reg=greg)
            lv = _g4.LogicalVolume(zone_solid,
                                   material,
                                   _random_name(),
                                   greg)

            pv = _g4.PhysicalVolume(list(zone.tbxyz()),
                                    list(zone.centre()),
                                    lv,
                                    _random_name(),
                                    wlv, greg)

            extents.append(wlv.extent())
        return extents


def _get_relative_rot_matrix(first, second):
    return first.rotation().T.dot(second.rotation())

def _get_relative_translation(first, second):
    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    offset_vector = second.centre() - first.centre()
    mat = first.rotation().T
    offset_vector = mat.dot(offset_vector).view(Three)
    return offset_vector

def _get_relative_rotation(first, second):
    # The first solid is unrotated in a boolean operation, so it
    # is in effect rotated by its inverse.  We apply this same
    # rotation to the second solid to get the correct relative
    # rotation.
    return matrix2tbxyz(_get_relative_rot_matrix(first, second))

def _get_tra2(first, second):
    relative_angles = _get_relative_rotation(first, second)
    relative_translation = _get_relative_translation(first, second)
    relative_transformation = [relative_angles, relative_translation]
    # convert to the tra2 format of a list of lists...

    relative_transformation = [list(relative_transformation[0]),
                               list(relative_transformation[1])]
    return relative_transformation

def _random_name():
    return "a{}".format(uuid4()).replace("-", "")

def _make_wlv(reg):
    world_material = _g4.MaterialPredefined("G4_Galactic")
    world_solid = _g4.solid.Box("world_box", 100, 100, 100, reg, "mm")
    return _g4.LogicalVolume(world_solid, world_material, "world_lv", reg)

def are_extents_overlapping(extent1, extent2):
    lower1 = Three(extent1[0])
    upper1 = Three(extent1[1])
    lower2 = Three(extent2[0])
    upper2 = Three(extent2[1])

    return not any([upper1.x < lower2.x,
                    lower1.x > upper2.x,
                    upper1.y < lower2.y,
                    lower1.y > upper2.y,
                    upper1.z < lower2.z,
                    lower1.z > upper2.z])

def _get_zone_overlap(zone1, zone2):
    greg = _g4.Registry()

    solid1 = zone1.geant4_solid(greg)
    solid2 = zone2.geant4_solid(greg)

    tra2 = _get_tra2(zone1, zone2)

    intersection = _g4.solid.Intersection(_random_name(),
                           solid1,
                           solid2,
                           tra2,
                           greg)

    try:
        mesh = intersection.pycsgmesh()
    except NullMeshError:
        return None
    return mesh
