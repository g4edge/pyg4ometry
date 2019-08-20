import numpy as _np

from Vector import Three as _Three

import pyg4ometry.transformation as _trans
import pyg4ometry.geant4 as _g4

class Body(object):
    """A class representing a body as defined in FLUKA. gdml_solid()
    returns the body as a pygdml.solid.

    """

    def __init__(self):
        pass


class RPP(Body):
    """An RPP is a rectangular parallelpiped (a cuboid). """

    def __init__(self,name, xmin, xmax, ymin, ymax, zmin, zmax, expansion = 1.0, translation = [0,0,0], rotdefi = None, flukaregistry=None):
        self.name  = name
        self.lower = _Three([xmin, ymin, zmin])
        self.upper = _Three([xmax, ymax, zmax])

    def centre(self):
        return [self.lower[0] + 0.5*(self.upper[0]-self.lower[0]),
                self.lower[1] + 0.5*(self.upper[1]-self.lower[1]),
                self.lower[2] + 0.5*(self.upper[2]-self.lower[2])]

    def rotation(self):
        return [0,0,0]

    def geant4_solid(self, reg):
        self.g4_solid =  _g4.solid.Box(self.name,
                                       self.upper[0]-self.lower[0],
                                       self.upper[1]-self.lower[1],
                                       self.upper[2]-self.lower[2],
                                       reg,
                                       lunit="mm")
        return self.g4_solid

class BOX(Body):
    def __init__(self, name, v, h1, h2, h3):
        self.name = name
        self.v    = _Three(v)
        self.h1   = _Three(h1)
        self.h2   = _Three(h2)
        self.h3   = _Three(h3)

        if self.h1.dot(self.h2) != 0.0 or self.h1.dot(self.h3) != 0 or self.h2.dot(self.h3) != 0.0:
            print "not orthogonal" #TODO raise exception

    def centre(self):
        return self.v+(self.h1+self.h2+self.h3)*0.5

    def rotation(self):
        return [0,0,0]

    def geant4_solid(self):
        self.g4_solid =  _g4.solid.Box(self.name,
                                       self.h1.length(),
                                       self.h2.length(),
                                       self.h3.length(),
                                       reg,
                                       lunit="mm")

class SPH(Body):
    """A sphere"""

    def __init__(self, name, point, radius):
        self.name = name
        self.point = point
        self.radius = radius

    def centre(self):
        return point

    def rotation(self):
        v1 = _np.array([1,0,0])
        v2 = _np.array(self.h1)

        tm  = _trans.matrix2tbxyz(_trans.matrix_from([1,0,0],self.h1))
        return tm

    def geant4_solid(self, reg):
        self.g4_solid = _g4.solid.Orb(self.name,
                                      self.radius,
                                      reg,
                                      lunit="mm")
        return self.g4_solid

class RCC(Body):
    """Right circular cylinder"""

    def __init__(self, name, v, h1, r):
        self.name = name
        self.v    = v
        self.h1    = h1
        self.r    = r

    def centre(self):
        pass

    def rotation(self):
        pass

    def geant4_solid(self):
        pass

class REC(Body):
    """Right elliptical cylinder"""

    def __init__(self, name, v, h, r1, r2):
        self.name = name
        self.v    = v
        self.h    = h
        self.r1   = r1
        self.r2   = r2

    def centre(self):
        pass

    def rotation(self):
        pass

    def geant4_solid(self):
        pass
