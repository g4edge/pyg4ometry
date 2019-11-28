import logging
import pyg4ometry.geant4 as _g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix
from pyg4ometry.fluka.Body import Body as _Body
from .Vector import Three
from uuid import uuid4



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
        body0 = self.intersections[0].body
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

class Region(object):

    def __init__(self, name):
        self.name = name
        self.zones = []

    def addZone(self,zone):
        self.zones.append(zone)

    def centre(self):
        return self.zones[0].centre()

    def tbxyz(self):
        return self.zones[0].tbxyz()

    def rotation(self):
        return self.zones[0].rotation()

    def geant4_solid(self, reg):

        zone0 = self.zones[0]
        result = zone0.geant4_solid(reg)

        for zone,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):
            zone_name = "{}_union_z{}".format(self.name, i)

            print i, zone_name
            tra2 = _get_tra2(zone0, zone)

            result  = _g4.solid.Union(zone_name, result,
                                      zone.geant4_solid(reg),
                                      tra2,
                                      reg)
            logger.debug("union tra2 = %s", tra2)

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

def _get_relative_rot_matrix(first, second):
    return first.rotation().T.dot(second.rotation())

def _get_relative_translation(first, second):
    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    offset_vector = second.centre() - first.centre()
    mat = first.rotation() # don't invert this  don't know why.  something
    # changed internally in pyg4ometry i think.  this works.
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
