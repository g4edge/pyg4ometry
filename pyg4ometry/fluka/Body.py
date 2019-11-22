import numpy as _np
from Vector import Three as _Three

import pyg4ometry.transformation as _trans
import pyg4ometry.geant4 as _g4

import logging
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

INFINITY = 500

class Body(object):
    """A class representing a body as defined in FLUKA. gdml_solid()
    returns the body as a pygdml.solid.

    """

    def __init__(self):
        pass

    def addToRegistry(self, flukaregistry):
        if flukaregistry is not None:
            flukaregistry.addBody(self)

    def tbxyz(self):
        return _trans.matrix2tbxyz(self.rotation())



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
        return _np.identity(3)

    def geant4_solid(self, reg):
        self.g4_solid =  _g4.solid.Box(self.name,
                                       self.upper[0]-self.lower[0],
                                       self.upper[1]-self.lower[1],
                                       self.upper[2]-self.lower[2],
                                       reg,
                                       lunit="mm")
        return self.g4_solid

    def __repr__(self):
        return ("<RPP: {s.name},"
                " x0={s.xmin}, x1={s.xmax},"
                " y0={s.ymin}, y1={s.ymax},"
                " z0={s.zmin}, z1={s.zmax}>").format(s=self)

class BOX(Body):
    def __init__(self, name, vertex, edge1, edge2, edge3, flukaregistry=None):
        self.name = name
        self.vertex    = _Three(vertex)
        self.edge1   = _Three(edge1)
        self.edge2   = _Three(edge2)
        self.edge3   = _Three(edge3)

        _raise_if_not_all_mutually_perpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutally orthogonal.")

    def centre(self):
        return self.vertex + 0.5 * (self.edge1 + self.edge2 + self.edge3)

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, greg):
        return _g4.solid.Box(self.name,
                             self.edge1.length(),
                             self.edge2.length(),
                             self.edge3.length(),
                             greg,
                             lunit="mm")

    def __repr__(self):
        v = self.vertex
        e1 = self.edge1
        e2 = self.edge2
        e3 = self.edge3
        return ("<BOX: {}, v=({}, {}, {}),"
                " e1=({}, {}, {}),"
                " e2=({}, {}, {}), "
                " e3=({}, {}, {})>").format(self.name,
                                            v.x, v.y, v.z,
                                            e1.x, e1.y, e1.z,
                                            e2.x, e2.y, e2.z,
                                            e3.x, e3.y, e3.z)


class ELL(Body):
    """Ellipsoid of revolution.
    focus1 = location of one of the foci on the major ellipsoid axis
    focus2 = location of the other focus on the major ellipsoid axis
    length = full length of the major ellipsoid axis
    """

    def __init__(self, name, focus1, focus2, length, flukaregistry=None):
        self.name = name
        self.focus1 = _Three(focus1)
        self.focus2 = _Three(focus2)
        self.length = length # major axis length

        # semi-major axis should be greater than the distances to the
        # foci from the centre (aka the linear eccentricity).
        if (0.5*self.length <= (self.focus1 - self.centre()).length()
            or 0.5*self.length <= (self.focus2 - self.centre()).length()):
            raise ValueError("Distance from foci to centre must be"
                             " smaller than the semi-major axis length.")

    def centre(self):
        return 0.5 * (self.focus1 + self.focus2)

    def rotation(self):
        # TODO: ELL is underconstrained, there is some convention
        # baked into FLUKA that I must recreate here to get the
        # correct rotation around the semi-major axis.
        initial = [1, 0, 0]  # foci start pointing along x (we choose)
        # initial2 = [0, 1, 0]  # semiminor starts pointing along y.
        final = self.focus1 - self.focus2
        # final2 =
        # return _two_fold_orientation(initial1, final1, initial2, final2)
        return _trans.matrix_from(initial, final).T # .T fudge factor

    def geant4_solid(self, greg):
        centre = self.centre()
        linear_eccentricity = (self.focus1 - self.centre()).length()
        semiminor = _np.sqrt((0.5*self.length)**2 - linear_eccentricity**2)
        # We choose the x-z plane as the plane of the ellipse that
        # gives the ellipsoid of rotation.  So the semi-minor is in y.
        return _g4.solid.Ellipsoid(self.name,
                                   0.5 * self.length,
                                   semiminor,
                                   0.5 * self.length,
                                   -self.length, # cuts, we don't cut.
                                   self.length,
                                   greg)


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
        return rotation.T # invert rotation fudge factor to make it work

    def geant4_solid(self, reg):
        return _g4.solid.Tubs(self.name,
                              0.0,
                              self.radius,
                              self.direction.length(),
                              0.0,
                              2*_np.pi,
                              reg,
                              lunit="mm")

    def __repr__(self):
        f = self.face
        d = self.direction
        return ("<RCC: {}, face=({}, {}, {}),"
                " dir=({}, {}, {}),"
                " r={}>").format(self.name,
                                 f.x, f.y, f.z,
                                 d.x, d.y, d.z,
                                 self.radius)

class REC(Body):
    """Right circular cylinder
    face = centre of one of the faces
    direction = vector pointing from one face to the other.
                the magnitude of this vector is the cylinder length.
    semiminor = vector pointing in the direction of the ellipse
                semi-minor axis.  its magnitude is the length of the
                semi-minor axis of the ellipse.
    semimajor = vector pointing in the direction of the semimajor axis.  its
                magnitude is the length of semi-major axis of the ellipse.
    """

    def __init__(self, name, face, direction, semiminor, semimajor,
                 flukaregistry=None):
        self.name = name
        self.face = _Three(face)
        self.direction = _Three(direction)
        self.semiminor = _Three(semiminor)
        self.semimajor = _Three(semimajor)

        _raise_if_not_all_mutually_perpendicular(
            self.direction, self.semiminor, semimajor,
            ("Direction, semiminor, and semimajor are"
             " not all mutually perpendicular."))

        self.addToRegistry(flukaregistry)

    def centre(self):
        return self.face + 0.5 * self.direction

    def rotation(self):
        initial_direction = [0, 0, 1]
        initial_semiminor = [1, 0, 0]

        final_direction = self.direction
        final_semiminor = self.semiminor
        rotation = _trans.two_fold_orientation(initial_direction,
                                               final_direction,
                                               initial_semiminor,
                                               final_semiminor)
        return rotation.T # invert rotation fudge factor to make it work

    def geant4_solid(self, reg):
        return _g4.solid.EllipticalTube(self.name,
                                        2 * self.semiminor.length(),
                                        2 * self.semimajor.length(),
                                        self.direction.length(),
                                        reg,
                                        lunit="mm")

    def __repr__(self):
        f = self.face
        d = self.direction
        m0 = self.semiminor
        m1 = self.semimajor
        return ("<REC: {}, face=({}, {}, {}),"
                " dir=({}, {}, {}),"
                " semimin=({}, {}, {}),"
                " semimaj=({}, {}, {})>").format(self.name,
                                                 f.x, f.y, f.z,
                                                 m0.x, m0.y, m0.z,
                                                 m1.x, m1.y, m1.z,
                                                 d.x, d.y, d.z)


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
        rotation = rotation.T # invert rotation matrix fudge to make it work
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

    def __repr__(self):
        m = self.major_centre
        d = self.direction
        return ("<TRC: {}, major=({}, {}, {}),"
                " direction=({}, {}, {}),"
                " rmaj={}, rmin={}>").format(self.name,
                                             m.x, m.y, m.z,
                                             d.x, d.y, d.z,
                                             self.major_radius,
                                             self.minor_radius)


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
        return _np.identity(3)

    def centre(self):
        return self.point

    def geant4_solid(self, reg):
        """Construct a solid, whole, geant4 sphere from this."""
        return _g4.solid.Orb(self.name,
                             self.radius,
                             reg,
                             lunit="mm")

    def __repr__(self):
        c = self.centre()
        return "<SPH: {}, centre=({},{},{}, r={})>".format(self.name,
                                                           c.x, c.y, c.z,
                                                           self.radius)


class HalfSpace(Body):
    def rotation(self):
        return _np.identity(3)

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
        return centre

    def __repr__(self):
        return "<XYP: {}, z={}>".format(self.name, self.z)


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
        return centre

    def __repr__(self):
        return "<XZP: {}, y={}>".format(self.name, self.y)


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
        return centre

    def __repr__(self):
        return "<YZP: {}, x={}>".format(self.name, self.x)


class InfiniteCylinder(Body):
    def geant4_solid(self, registry):
        return _g4.solid.Tubs(self.name,
                              0.0,
                              self.radius,
                              INFINITY,
                              0.0, 2*_np.pi,
                              registry,
                              lunit="mm")


class XCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to x-axis

    y = y-coordinate of the centre of the cylinder
    z = z-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """

    def __init__(self, name, y, z, radius,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.y = y
        self.z = z
        self.radius = radius

    def centre(self):
        return _Three(0.0, self.y, self.z)

    def rotation(self):
        return _np.array([[0, 0, -1],
                          [0, 1, 0],
                          [1, 0, 0]])

    def __repr__(self):
        return "<XCC: {}, y={}, z={}>".format(self.name, self.y, self.z)


class YCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to y-axis

    z = z-coordinate of the centre of the cylinder
    x = x-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """

    def __init__(self, name, z, x, radius,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.z = z
        self.x = x
        self.radius = radius


    def centre(self):
        return _Three(self.x, 0.0, self.z)

    def rotation(self):
        return _np.array([[1, 0, 0],
                          [0, 0, 1],
                          [0, -1, 0]])

    def __repr__(self):
        return "<YCC: {}, z={}, x={}>".format(self.name, self.z, self.x)


class ZCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to z-axis

    x = x-coordinate of the centre of the cylinder
    y = y-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """

    def __init__(self, name, x, y, radius,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius

    def centre(self):
        return _Three(self.x, self.y, 0.0)

    def rotation(self):
        return _np.identity(3)

    def __repr__(self):
        return "<ZCC: {}, x={}, y={}>".format(self.name, self.x, self.y)


class XEC(Body):
    """Infinite elliptical cylinder parallel to x-axis

    y = y-coordinate of the centre of the cylinder
    z = z-coordinate of the centre of the cylinder
    ysemi = semi-axis of the ellipse face in the y-directiony
    zsemi = semi-axis of the ellipse face in the z-direction

    """

    def __init__(self, name, y, z, ysemi, zsemi,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.y = y
        self.z = z
        self.ysemi = ysemi
        self.zsemi = zsemi

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(0.0, self.y, self.z)

    def rotation(self):
        return _np.array([[0, 0, -1],
                          [0, 1, 0],
                          [1, 0, 0]])

    def geant4_solid(self, reg):
        return _g4.solid.EllipticalTube(self.name,
                                        2 * self.zsemi, # full width, not semi
                                        2 * self.ysemi,
                                        INFINITY,
                                        reg,
                                        lunit="mm")


    def __repr__(self):
        return "<XEC: {}, y={}, z={}, ysemi={}, zsemi={}>".format(
            self.name,
            self.y, self.z,
            self.ysemi, self.zsemi)


class YEC(Body):
    """Infinite elliptical cylinder parallel to y-axis

    z = z-coordinate of the centre of the cylinder
    y = y-coordinate of the centre of the cylinder
    ysemi = semi-axis of the ellipse face in the y-directiony
    zsemi = semi-axis of the ellipse face in the z-direction

    """

    def __init__(self, name, z, x, zsemi, xsemi,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.z = z
        self.x = x
        self.zsemi = zsemi
        self.xsemi = xsemi

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(self.x, 0.0, self.z)


    def rotation(self):
        return _np.array([[1, 0, 0],
                          [0, 0, 1],
                          [0, -1, 0]])

    def geant4_solid(self, reg):
        return _g4.solid.EllipticalTube(self.name,
                                        2 * self.xsemi, # full width, not semi
                                        2 * self.zsemi,
                                        INFINITY,
                                        reg,
                                        lunit="mm")

    def __repr__(self):
        return "<YEC: {}, z={}, x={}, zsemi={}, xsemi={}>".format(
            self.name,
            self.z, self.x,
            self.zsemi, self.xsemi)


class ZEC(Body):
    """Infinite elliptical cylinder parallel to z-axis

    z = z-coordinate of the centre of the cylinder
    y = y-coordinate of the centre of the cylinder
    ysemi = semi-axis of the ellipse face in the y-directiony
    zsemi = semi-axis of the ellipse face in the z-direction

    """

    def __init__(self, name, x, y, xsemi, ysemi,
                 expansion=None,
                 translation=None,
                 rotdefi=None,
                 flukaregistry=None):
        self.name = name
        self.x = x
        self.y = y
        self.xsemi = xsemi
        self.ysemi = ysemi

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(self.x, self.y, 0.0)

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, reg):
        return _g4.solid.EllipticalTube(self.name,
                                        2 * self.xsemi, # full width, not semi
                                        2 * self.ysemi,
                                        INFINITY,
                                        reg,
                                        lunit="mm")

    def __repr__(self):
        return "<ZEC: {}, x={}, y={}, xsemi={}, ysemi={}>".format(
            self.name,
            self.x, self.y,
            self.xsemi, self.ysemi)


class PLA(Body):
    """Generic half-space.

    Parameters:
    point = point on surface of halfspace
    normal = vector normal to the surface (pointing outwards from the
             contents of the body)
    """

    def __init__(self, name, normal, point, flukaregistry=None):
        self.name = name
        self.normal = _Three(normal)
        self.point = _Three(point)

        # normalise it if it is not normalised.
        self.normal = self.normal / _np.linalg.norm(self.normal)

    def centre(self):
        return self.point - 0.5 * INFINITY * self.normal.unit()

    def rotation(self):
        # Choose the face pointing in the direction of the positive
        # z-axis to make the surface of the half space.
        return _trans.matrix_from([0, 0, 1], self.normal)

    def geant4_solid(self, reg):
        return _g4.solid.Box(self.name,
                             INFINITY,
                             INFINITY,
                             INFINITY,
                             reg,
                             lunit="mm")


def _raise_if_not_all_mutually_perpendicular(first, second, third, message):
    if (first.dot(second) != 0.0
        or first.dot(third) != 0
        or second.dot(third) != 0.0):
        raise ValueError(message)
