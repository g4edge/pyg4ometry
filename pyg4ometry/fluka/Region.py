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

    def geant4_solid(self, reg):

        b             = self.boolean[0].body.geant4_solid(reg)
        rotation = self.rotation()
        centre   = self.centre()
        tra1 = [rotation, centre]

        for s,i in zip(self.boolean[1:],range(0,len(self.boolean[1:])+2)):
            bName = "s"+str(i)
            print i,bName
            tra2 = [list(s.body.rotation()), list(s.body.centre())]
            relative_tra = _get_relative_tra(tra1, tra2)
            b2 = s.body.geant4_solid(reg)
            if isinstance(s, Subtraction):
                b  =_g4.solid.Subtraction(bName,
                                          b, b2,
                                          relative_tra, reg)

            elif isinstance(s, Intersection):
                b  =_g4.solid.Intersection(bName,
                                           b, b2,
                                           relative_tra, reg)

        return b

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

    def rotation(self):
        return self.zones[0].rotation()

    def geant4_solid(self, reg):

        z = self.zones[0].geant4_solid(reg)
        centre   = self.centre()
        rotation = self.rotation()
        tra1 = [rotation, centre]

        for z_other,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):
            zName = "z"+str(i)
            print i, zName
            tra2 = [list(z_other.rotation()), list(z_other.centre())]
            relative_tra = _get_relative_tra(tra1, tra2)
            z  =_g4.solid.Union(zName, z,
                                z_other.geant4_solid(reg),
                                relative_tra,
                                reg)

        return z

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

def _get_relative_tra(tra1, tra2):
    # rotations
    rot1 = tra1[0]
    rot2 = tra2[0]
    # translations
    trl1 = Three(tra1[1])
    trl2 = Three(tra2[1])

    # The first solid is unrotated in a boolean operation, so it
    # is in effect rotated by its inverse.  We apply this same
    # rotation to the /second/ solid to get the correct relative
    # rotation.  (recall inverse of a rotation matrix = its transpose)
    rot1 = tbxyz2matrix(rot1)
    rot2 = tbxyz2matrix(rot2)
    relative_rot_matrix = rot1.T.dot(rot2)

    # In a boolean rotation, the first solid is centred on zero,
    # so to get the correct offset, subtract from the second the
    # first, and then rotate this offset with the rotation matrix.
    relative_trl = trl2 - trl1
    relative_trl = rot1.T.dot(relative_trl).view(Three)

    rel_rot = matrix2tbxyz(relative_rot_matrix)

    # convert to Three to list to make code in Defines.py happy.
    return [rel_rot, list(relative_trl)]
