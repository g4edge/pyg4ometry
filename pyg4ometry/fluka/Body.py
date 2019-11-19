import numpy as _np
from Vector import Three as _Three

import pyg4ometry.transformation as _trans
import pyg4ometry.geant4 as _g4

INFINITY = 50

class Body(object):
    """A class representing a body as defined in FLUKA. gdml_solid()
    returns the body as a pygdml.solid.

    """

    def __init__(self):
        pass

    def addToRegistry(self, flukaregistry):
        if flukaregistry is not None:
            flukaregistry.addBody(self)



class RPP(Body):
    """An RPP is a rectangular parallelpiped (a cuboid). """

    def __init__(self, name,
                 xmin, xmax,
                 ymin, ymax,
                 zmin, zmax,
                 expansion=1.0,
                 translation=[0,0,0],
                 rotdefi=None,
                 flukaregistry=None):
        self.name  = name
        self.lower = _Three([xmin, ymin, zmin])
        self.upper = _Three([xmax, ymax, zmax])

        self.addToRegistry(flukaregistry)

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

class RCC(Body):
    """Right circular cylinder
    face = centre of one of the faces
    direction = vector pointing from one face to the other.
                the magnitude of this vector is the cylinder length.
    radius = radius of the cylinder face
    """

    def __init__(self, name, face, direction, radius, flukaregistry=None):
        self.name = name
        self.face = _Three(face)
        self.direction = _Three(direction)
        self.radius = radius

        self.addToRegistry(flukaregistry)

    def centre(self):
        return self.face + 0.5 * self.direction

    def rotation(self):
        initial = [0, 0, 1]
        final = self.direction

        rotation = _trans.matrix_from(initial, final)
        # WHY DO I DO THIS????????
        rotation = _np.linalg.inv(rotation)
        rotation = _trans.matrix2tbxyz(rotation)
        return rotation

    def geant4_solid(self, reg):
        return _g4.solid.Tubs(self.name,
                              0.0,
                              self.radius,
                              self.direction.length(),
                              0.0,
                              2*_np.pi,
                              reg,
                              lunit="mm")


class TRC(Body):
    """Truncated Right-angled Cone.

    centre: coordinates of the centre of the larger face.
    direction: coordinates of the vector pointing from major to minor.
    radius_major: radius of the larger face.
    radius_minor: radius of the smaller face.
    """
    def __init__(self,
                 name,
                 major_centre,
                 direction,
                 major_radius,
                 minor_radius,
                 translation=None,
                 flukaregistry=None):
        self.name = name
        self.major_centre = _Three(major_centre)
        if translation is not None:
            self.major_centre += _Three(translation)
        self.direction = _Three(direction)
        self.major_radius = major_radius
        self.minor_radius = minor_radius

        self.addToRegistry(flukaregistry)

    def rotation(self):
        # We choose in the as_gdml_solid method to place the major at
        # -z, and the major at +z:
        rotation = _trans.matrix_from([0, 0, 1], self.direction)
        rotation = _np.linalg.inv(rotation)
        rotation = _trans.matrix2tbxyz(rotation)
        return rotation

    def centre(self):
        return self.major_centre + 0.5 * self.direction

    def geant4_solid(self, registry):
        # The first face of _g4.Cons is located at -z, and the
        # second at +z.  Here choose to put the major face at -z.
        return _g4.solid.Cons(self.name,
                              0.0, self.major_radius,
                              0.0, self.minor_radius,
                              self.direction.length(),
                              0.0, 2*_np.pi,
                              registry,
                              lunit="mm")


class SPH(Body):
    """A sphere.

    point = centre of sphere
    radius = radius of sphere
    """
    def __init__(self, name, point, radius, flukaregistry=None):
        self.name = name
        self.point = _Three(point)
        # if translation is not None:
        #     self.point += _Three(translation)
        self.radius = radius


        self.addToRegistry(flukaregistry)

    def rotation(self):
        # self.rotation = _np.identity(3)
        return [0, 0, 0]

    def centre(self):
        return self.point

    def geant4_solid(self, reg):
        """Construct a solid, whole, geant4 sphere from this."""
        return _g4.solid.Orb(self.name,
                             self.radius,
                             reg,
                             lunit="mm")


class HalfSpace(Body):
    def rotation(self):
        # return _np.identity(3)
        return [0, 0, 0]

    def geant4_solid(self, registry):
        return _g4.solid.Box(self.name,
                             INFINITY,
                             INFINITY,
                             INFINITY,
                             registry)


class XYP(HalfSpace):
    """Infinite half space perpendicular to the z-axis."""
    def __init__(self, name, z, translation=None, flukaregistry=None):
        self.name = name
        self.z = z
        # if translation is not None:
        #     self.z += translation[2]
        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre =  transverseOffset + _Three(0, 0, self.z - (INFINITY * 0.5))
        print "{}, centre =".format(self.name),centre, self
        return centre

class XZP(HalfSpace):
    """Half space perpendicular to the y-axis."""
    def __init__(self, name, y, translation=None, flukaregistry=None):
        self.name = name
        self.y = y
        # if translation is not None:
        #     self.y += translation[1]

        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre = transverseOffset + _Three(0, self.y - (INFINITY * 0.5), 0)
        print "{}, centre =".format(self.name),centre, self
        return centre

class YZP(HalfSpace):
    """Infinite half space perpendicular to the x-axis."""
    def __init__(self, name, x, translation=None, flukaregistry=None):
        self.name = name
        self.x = x
        # if translation is not None:
        #     self.x += translation[0]
        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre = transverseOffset + _Three(self.x - (INFINITY * 0.5), 0, 0)
        print "{}, centre =".format(self.name),centre, self
        return centre
