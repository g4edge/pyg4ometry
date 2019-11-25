import pyg4ometry.geant4 as _g4
from pyg4ometry.transformation import matrix2tbxyz, tbxyz2matrix
from .Vector import Three



class Subtraction(object):
    def __init__(self, body):
        self.body = body

class Intersection(object):
    def __init__(self, body):
        self.body = body

class Union(object):
    def __init__(self, body):
        self.body = body

class Zone(object):
    def __init__(self):
        self.boolean = []

    def addSubtraction(self, body):
        self.boolean.append(Subtraction(body))

    def addIntersection(self,body):
        self.boolean.append(Intersection(body))

    def centre(self):
        return self.boolean[0].body.centre()

    def rotation(self):
        return self.boolean[0].body.rotation()

    def tbxyz(self):
        return matrix2tbxyz(self.rotation())

    def geant4_solid(self, reg):

        body0 = self.boolean[0].body
        result = body0.geant4_solid(reg)

        for boolean,i in zip(self.boolean[1:],range(0,len(self.boolean[1:])+2)):
            bName = "s"+str(i)
            print i,bName
            tra2 = _get_tra2(body0, boolean.body)

            other_solid = boolean.body.geant4_solid(reg)
            if isinstance(boolean, Subtraction):
                result  =_g4.solid.Subtraction(bName,
                                               result, other_solid,
                                               tra2, reg)

            elif isinstance(boolean, Intersection):
                result  =_g4.solid.Intersection(bName,
                                                result, other_solid,
                                                tra2, reg)

        return result

    def fluka_free_string(self):
        fs = ""

        for s in self.boolean :
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
            zone_name = "z"+str(i)
            print i, zone_name
            tra2 = _get_tra2(zone0, zone)

            result  = _g4.solid.Union(zone_name, result,
                                      zone.geant4_solid(reg),
                                      tra2,
                                      reg)

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
    relative_translation = [list(relative_translation[0]),
                            list(relative_translation[1])]
    return relative_transformation
