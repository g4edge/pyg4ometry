from contextlib import contextmanager
import logging
from itertools import chain

import numpy as np
import vtk

from .vector import Three
from pyg4ometry.pycsg.core import CSG as _CSG
import pyg4ometry.pycsg.geom as _geom
import pyg4ometry.transformation as trans
import pyg4ometry.geant4 as g4
import pyg4ometry.exceptions
from .directive import Transform
from .vector import Extent as _Extent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_DEFAULT_INFINITY = 50000000
INFINITY = _DEFAULT_INFINITY
LENGTH_SAFETY = 1e-6


@contextmanager
def infinity(inf):
    """Use this to temporarily modify INFINITY, with it resetting back
    to the default once the block has exited.  INFINITY is used
    throughout the bodies to approximate the infinite size of infinity
    (elliptical) cylinders, half spaces, and quadrics.

    :param inf: the value to temporarily set INFINITY to."""
    global INFINITY
    INFINITY = inf
    try:
        yield inf
    finally:
        INFINITY = _DEFAULT_INFINITY


class BodyMixin(object):
    """
    Base class representing a body as defined in FLUKA
    """
    def addToRegistry(self, flukaregistry):
        if flukaregistry is not None:
            flukaregistry.addBody(self)

    def tbxyz(self):
        return trans.matrix2tbxyz(self.rotation())

    # in the per body _withLengthSafety methods below, factor =
    # -1*LENGTH_SAFETY should make the body small in
    # _withLengthSafety, and +LENGTH_SAFETY must make the body
    # bigger.
    def safetyExpanded(self, reg=None):
        return self._withLengthSafety(LENGTH_SAFETY, reg)

    def safetyShrunk(self, reg=None):
        return self._withLengthSafety(-LENGTH_SAFETY, reg)

    def _set_transform(self, transform):
        if transform is None: # identity transform
            return Transform()
        return transform

    def _extent_to_scale_factor(self, extent):
        if extent is None: # if no extent then just use the global constant.
            return INFINITY
        else:
            # Multiply by sqrt(3) to account for any rotations of the body
            # within the extent so that the body is definitely big enough.
            return max(extent.size * 1.5 * np.sqrt(3))

    def _extent_to_offset(self, extent):
        if extent is None:
            offset = Three(0, 0, 0)
        elif extent is not None:
            offset = extent.centre
        else:
            raise TypeError("Unknown type of extent {}".format(extent))
        return offset


class _HalfSpaceMixin(BodyMixin):
    # Base class for XYP, XZP, YZP.
    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, registry, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)
        return g4.solid.Box(self.name,
                            exp * scale,
                            exp * scale,
                            exp * scale,
                            registry)

    def _halfspaceFreeStringHelper(self, coordinate):
        typename = type(self).__name__
        return "{} {} {}".format(typename, self.name, coordinate)


class _InfiniteCylinderMixin(BodyMixin):
    # Base class for XCC, YCC, ZCC.
    def geant4Solid(self, registry, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)
        return g4.solid.Tubs(self.name,
                             0.0,
                             exp * self.radius,
                             scale * exp,
                             0.0, 2*np.pi,
                             registry,
                             lunit="mm")

    def _infCylinderFreestringHelper(self, coord1, coord2, coord3):
        typename = type(self).__name__
        return "{} {} {} {} {}".format(typename, self.name, coord1, coord2, coord3)


class RPP(BodyMixin):
    """Rectangular Parallelepiped

    :param name: of body
    :type name: str
    :param xmin: lower x coordinate of RPP
    :type xmin: float
    :param xmax: upper x coordinate of RPP
    :type xmax: float
    :param ymin: lower y coordinate of RPP
    :type ymin: float
    :param ymax: upper y coordinate of RPP
    :type ymax: float
    :param zmin: lower z coordinate of RPP
    :type zmin: float
    :param zmax: upper z coordinate of RPP
    :type zmax: float

    """
    def __init__(self, name,
                 xmin, xmax, ymin, ymax, zmin, zmax,
                 transform=None, flukaregistry=None, addRegistry=True):
        self.name = name
        self.lower = Three([xmin, ymin, zmin])
        self.upper = Three([xmax, ymax, zmax])

        self.transform = self._set_transform(transform)

        if not all([xmin < xmax, ymin < ymax, zmin < zmax]):
            raise ValueError("Each of the xmin, ymin, zmin must be"
                             " smaller than the corresponding"
                             " xmax, ymax, zmax.")

        if addRegistry :
            self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(0.5 * (self.lower
                                                        + self.upper))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, reg, extent=None):
        v = self.transform.netExpansion() * (self.upper - self.lower)
        return g4.solid.Box(self.name,
                            v.x, v.y, v.z,
                            reg,
                            lunit="mm")

    def __repr__(self):
        l = self.lower
        u = self.upper
        return ("<RPP: {},"
                " x0={l.x}, x1={u.x},"
                " y0={l.y}, y1={u.y},"
                " z0={l.z}, z1={u.z}>").format(self.name, l=l, u=u)

    def _withLengthSafety(self, safety, reg):
        lower = self.lower - [safety, safety, safety]
        upper = self.upper + [safety, safety, safety]
        return RPP(self.name,
                   lower.x, upper.x,
                   lower.y, upper.y,
                   lower.z, upper.z,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "RPP {} {} {} {} {} {} {}".format(self.name,
                                                 str(self.lower[0]),
                                                 str(self.upper[0]),
                                                 str(self.lower[1]),
                                                 str(self.upper[1]),
                                                 str(self.lower[2]),
                                                 str(self.upper[2]))

class BOX(BodyMixin):
    """General Rectangular Parallelepiped

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the corners.
    :type vertex: list
    :param edge1: vector [x, y, z] denoting the first side of the box.
    :type edge1: list
    :param edge2: vector [x, y, z] denoting the second side of the box.
    :type edge2: list
    :param edge3: vector [x, y, z] denoting the second side of the box.
    :type edge3: list

    """
    def __init__(self, name, vertex, edge1, edge2, edge3, transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertex = Three(vertex)
        self.edge1 = Three(edge1)
        self.edge2 = Three(edge2)
        self.edge3 = Three(edge3)

        self.transform = self._set_transform(transform)

        _raiseIfNotAllMutuallyPerpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutally orthogonal.")

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector((self.vertex
                                                  + 0.5 * (self.edge1
                                                           + self.edge2
                                                           + self.edge3)))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, greg, extent=None):
        exp = self.transform.netExpansion()
        return g4.solid.Box(self.name,
                            exp * self.edge1.length(),
                            exp * self.edge2.length(),
                            exp * self.edge3.length(),
                            greg,
                            lunit="mm")

    def __repr__(self):
        return ("<BOX: {}, v={}, e1={}, e2={}, e3={}>").format(
            self.name,
            list(self.vertex),
            list(self.edge1), list(self.edge2), list(self.edge3))

    def _withLengthSafety(self, safety, reg):
        u1 = self.edge1.unit()
        u2 = self.edge2.unit()
        u3 = self.edge3.unit()
        new_vertex = self.vertex - (u1 + u2 + u3) * safety
        return BOX(self.name,
                   new_vertex,
                   self.edge1 + 2 * safety * u1,
                   self.edge2 + 2 * safety * u2,
                   self.edge3 + 2 * safety * u3,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        param_string = _iterablesToFreeString(self.vertex,
                                                 self.edge1,
                                                 self.edge2,
                                                 self.edge3)
        return "BOX {} {}".format(self.name, param_string)


class SPH(BodyMixin):
    """Sphere

    :param name: of body
    :type name: str
    :param point: position [x, y, z] of the centre of the sphere.
    :type point: list
    :param radius: radius of the sphere.
    :type radius: float

    """
    def __init__(self, name, point, radius, transform=None, flukaregistry=None):
        self.name = name
        self.point = Three(point)
        self.radius = radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(self.point)

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, reg, extent=None):
        return g4.solid.Orb(self.name,
                            self.transform.netExpansion() * self.radius,
                            reg,
                            lunit="mm")

    def __repr__(self):
        return "<SPH: {}, centre={}, r={})>".format(self.name,
                                                    list(self.centre()),
                                                    self.radius)

    def _withLengthSafety(self, safety, reg):
        return SPH(self.name, self.point, self.radius + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "SPH {} {} {}".format(self.name,
                                     _iterablesToFreeString(self.point),
                                     self.radius)


class RCC(BodyMixin):
    """

    Right Circular Cylinder

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the faces of the cylinder.
    :type vertex: list
    :param edge1: vector [x, y, z] denoting the direction along the \
    length of the cylinder.
    :type edge1: list
    :param edge2: radius of the cylinder face.
    :type edge2: float

    """
    def __init__(self, name, face, direction, radius, transform=None,
                 flukaregistry=None):
        self.name = name
        self.face = Three(face)
        self.direction = Three(direction)
        self.radius = radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(self.face
                                                 + 0.5 * self.direction)

    def rotation(self):
        initial = [0, 0, 1]
        final = self.direction
        rotation = trans.matrix_from(initial, final)
        return self.transform.leftMultiplyRotation(rotation)

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        return g4.solid.Tubs(self.name,
                             0.0,
                             exp * self.radius,
                             exp * self.direction.length(),
                             0.0,
                             2*np.pi,
                             reg,
                             lunit="mm")

    def __repr__(self):
        return ("<RCC: {}, face={}, dir={}, r={}>").format(
            self.name, list(self.face), list(self.direction), self.radius)

    def _withLengthSafety(self, safety, reg):
        unit = self.direction.unit()
        face = self.face - safety * unit
        # Apply double safety to the direction to account for the fact
        # that the face has been shifted by a single amount of
        # safety in the direction of the direction vector.
        direction = self.direction + 2 * safety * unit
        return RCC(self.name,
                   face, direction,
                   self.radius + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "RCC {} {} {}".format(self.name,
                                     _iterablesToFreeString(self.face,
                                                               self.direction),
                                     self.radius)


class REC(BodyMixin):
    """

    Right Elliptical Cylinder

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the faces of the cylinder.
    :type vertex: list
    :param semiminor: vector [x, y, z] denoting the direction along the \
    semiminor axis of the ellipse.
    :type semiminor: list
    :param semimajor: vector [x, y, z] denoting the direction along the \
    semimajor axis of the ellipse.
    :type semimajor: list

    """
    def __init__(self, name, face, direction, semiminor, semimajor,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.face = Three(face)
        self.direction = Three(direction)
        self.semiminor = Three(semiminor)
        self.semimajor = Three(semimajor)

        self.transform = self._set_transform(transform)

        _raiseIfNotAllMutuallyPerpendicular(
            self.direction, self.semiminor, semimajor,
            ("Direction, semiminor, and semimajor are"
             " not all mutually perpendicular."))

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(self.face
                                                 + 0.5 * self.direction)

    def rotation(self):
        initial_direction = [0, 0, 1]
        initial_semiminor = [1, 0, 0]

        final_direction = self.direction
        final_semiminor = self.semiminor
        rotation = trans.two_fold_orientation(initial_direction,
                                              final_direction,
                                              initial_semiminor,
                                              final_semiminor)
        return self.transform.leftMultiplyRotation(rotation)

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        return g4.solid.EllipticalTube(self.name,
                                       2 * exp * self.semiminor.length(),
                                       2 * exp * self.semimajor.length(),
                                       exp * self.direction.length(),
                                       reg,
                                       lunit="mm")

    def __repr__(self):
        return ("<REC: {}, face={}, dir={}, semimin={}, semimaj={}>").format(
            self.name,
            list(self.face), list(self.direction),
            list(self.semiminor), list(self.semimajor))

    def _withLengthSafety(self, safety, reg):
        direction_unit = self.direction.unit()
        face = self.face - safety * direction_unit
        # Apply double safety to the direction for the same reason as RCC.
        direction = self.direction + 2 * safety * direction_unit
        semiminor = self.semiminor + safety * self.semiminor.unit()
        semimajor = self.semimajor + safety * self.semimajor.unit()

        return REC(self.name, face,
                   direction,
                   semiminor,
                   semimajor,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "REC {} {}".format(self.name,
                                  _iterablesToFreeString(self.face,
                                                            self.direction,
                                                            self.semiminor,
                                                            self.semimajor))


class TRC(BodyMixin):
    """

    Truncated Right-angled Cone

    :param name: of body
    :type name: str
    :param major_centre: vector [x, y, z] position of the centre of the \
    larger face.
    :type major_centre: list
    :param direction: vector [x, y, z] pointing from the larger face \
    to the smaller face.
    :type direction: list
    :param major_radius: radius of the larger face.
    :type major_radius: float
    :param minor_radius: radius of the smaller face.
    :type minor_radius: float

    """
    def __init__(self, name, major_centre, direction,
                 major_radius, minor_radius,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.major_centre = Three(major_centre)
        self.direction = Three(direction)
        self.major_radius = major_radius
        self.minor_radius = minor_radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(self.major_centre
                                                 + 0.5 * self.direction)

    def rotation(self):
        # We choose in the as_gdml_solid method to place the major at
        # -z, and the major at +z:
        rotation = trans.matrix_from([0, 0, 1], self.direction)
        return self.transform.leftMultiplyRotation(rotation)

    def geant4Solid(self, registry, extent=None):
        # The first face of g4.Cons is located at -z, and the
        # second at +z.  Here choose to put the major face at -z.
        exp = self.transform.netExpansion()
        return g4.solid.Cons(self.name,
                             0.0, exp * self.major_radius,
                             0.0, exp * self.minor_radius,
                             exp * self.direction.length(),
                             0.0, 2*np.pi,
                             registry,
                             lunit="mm")

    def __repr__(self):
        return ("<TRC: {}, major={} direction={} rmaj={}, rmin={}>").format(
            self.name,
            list(self.major_centre),
            list(self.direction),
            self.major_radius,
            self.minor_radius)

    def _withLengthSafety(self, safety, reg):
        unit = self.direction.unit()
        major_centre = self.major_centre - safety * unit
        # Apply double safety for the same reason as we did with the RCC.
        direction = self.direction + 2 * safety * unit
        return TRC(self.name,
                   major_centre,
                   direction,
                   self.major_radius + safety,
                   self.minor_radius + safety,
                   transform=self.transform)

    def flukaFreeString(self):
        return "TRC {} {} {} {}".format(self.name,
                                        _iterablesToFreeString(
                                            self.major_centre,
                                            self.direction),
                                        self.major_radius,
                                        self.minor_radius)


class ELL(BodyMixin):
    """Ellipsoid of Revolution

    :param name: of body
    :type name: str
    :param focus1: position [x, y, z] denoting of one of the foci.
    :type focus1: list
    :param focus2: position [x, y, z] denoting the other focus.
    :type focus2: list
    :param length: length of the ellipse axis which the foci lie on.
    :type length: float

    """
    def __init__(self, name, focus1, focus2, length, transform=None,
                 flukaregistry=None):
        self.name = name
        self.focus1 = Three(focus1)
        self.focus2 = Three(focus2)
        self.length = length # major axis length

        self.transform = self._set_transform(transform)

        # semi-major axis should be greater than the distances to the
        # foci from the centre (aka the linear eccentricity).
        semimajor = 0.5 * self.transform.netExpansion() * self.length
        if (semimajor <= self._linearEccentricity()):
            raise ValueError("Distance from foci to centre must be"
                             " smaller than the semi-major axis length.")

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(0.5 * (self.focus1
                                                        + self.focus2))

    def rotation(self):
        initial = [0, 0, 1]  # major axis pointing along z
        final = self.focus1 - self.focus2
        return self.transform.leftMultiplyRotation(
            trans.matrix_from(initial, final))

    def _linearEccentricity(self):
        # Distance from centre to one of the foci.  This doesn't use
        # the .centre method as this ought to be independent of
        # location, whereas centre takes into account geometry directives.
        return (0.5 * self.transform.netExpansion()
                * (self.focus1 - self.focus2).length())

    def _semiminor(self):
        return np.sqrt((0.5 * self.transform.netExpansion() * self.length)**2 -
                       self._linearEccentricity()**2)

    def geant4Solid(self, greg, extent=None):
        semiminor = self._semiminor()
        expansion = self.transform.netExpansion()
        return g4.solid.Ellipsoid(self.name,
                                  semiminor,
                                  semiminor,
                                   # choose z to be the major.
                                  0.5 * expansion * self.length,
                                   # cuts, we don't cut:
                                  -self.length * expansion,
                                  self.length * expansion,
                                  greg)

    def __repr__(self):
        return "<ELL: {}, f1={}, f2={}, length={}>".format(
            self.name, list(self.focus1), list(self.focus2), self.length)

    def _withLengthSafety(self, safety, reg):
        centre = (self.focus1 + self.focus2) * 0.5

        # XXX: Dial up the safety so that the semiminor axes are
        # reduced sufficiently as well.  Maybe not ideal.
        ls_length = self.length + 10*safety

        return ELL(self.name,
                   self.focus1,
                   self.focus2,
                   ls_length,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "ELL {} {} {}".format(self.name,
                                     _iterablesToFreeString(self.focus1,
                                                               self.focus2),
                                     self.length)

class _WED_RAW(BodyMixin):
    # WED and RAW are aliases for one another, so we define it in a
    # single place and then inherit this class to provide the correct
    # type names below.
    def __init__(self, name, vertex, edge1, edge2, edge3, transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertex = Three(vertex)
        self.edge1 = Three(edge1)  # direction of the triangular face.
        self.edge2 = Three(edge2)  # direction of the triangular face.
        self.edge3 = Three(edge3)  # direction of length of the prism.

        self.transform = self._set_transform(transform)

        _raiseIfNotAllMutuallyPerpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutually perpendicular.")
        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        exp = self.transform.netExpansion()
        # need to determine the handedness of the three direction
        # vectors to get the correct vertex to use.
        crossproduct = np.cross(self.edge1, self.edge2)
        if trans.are_parallel(crossproduct, self.edge3):
            centre =  self.vertex
        elif trans.are_anti_parallel(crossproduct, self.edge3):
            centre = self.vertex + self.edge3
        else:
            raise ValueError(
                "Unable to determine if parallel or anti-parallel.")
        return self.transform.leftMultiplyVector(centre)

    def rotation(self):
        initial1 = [1, 0, 0] # edge1 starts off pointing in the x-direction.
        initial2 = [0, 1, 0] # edge3 starts off pointing in the y-direction.
        rotation =  trans.two_fold_orientation(initial1, self.edge1.unit(),
                                               initial2, self.edge2.unit())
        return self.transform.leftMultiplyRotation(rotation)

    def geant4Solid(self, greg, extent=None):
        exp = self.transform.netExpansion()
        face = [[0, 0],
                [exp * self.edge1.length(), 0],
                [0, exp * self.edge2.length()]]

        return g4.solid.ExtrudedSolid(self.name,
                                      face,
                                      [[0, [0, 0], 1],
                                       [exp * self.edge3.length(), [0, 0], 1]],
                                      registry=greg)

    def __repr__(self):
        return ("<{}: {}, v={}, e1={}, e2={}, e3={}>").format(
            type(self).__name__, # Can be either WED or RAW
            self.name,
            list(self.vertex),
            list(self.edge1),
            list(self.edge2),
            list(self.edge3))

    def _withLengthSafety(self, safety, reg):
        ctor = type(self) # return WED or RAW, not _WED_RAW.
        u1 = self.edge1.unit()
        u2 = self.edge2.unit()
        u3 = self.edge3.unit()
        new_vertex = self.vertex - (u1 + u2 + u3) * safety
        return ctor(self.name,
                    new_vertex,
                    self.edge1 + 2 * safety * u1,
                    self.edge2 + 2 * safety * u2,
                    self.edge3 + 2 * safety * u3,
                    transform=self.transform,
                    flukaregistry=reg)

    def flukaFreeString(self):
        typename = type(self).__name__
        return "{} {} {}".format(typename, self.name,
                                 _iterablesToFreeString(self.vertex,
                                                           self.edge1,
                                                           self.edge2,
                                                           self.edge3))


class WED(_WED_RAW):
    """Right Angle Wedge

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the the rectangular corners.
    :type vertex: list
    :param edge1: vector [x, y, z] denoting height of the wedge.
    :type edge1: list
    :param edge2: vector [x, y, z] denoting width of the wedge.
    :type edge2: list
    :param edge3: vector [x, y, z] denoting length of the wedge.
    :type edge3: list
    """


class RAW(_WED_RAW):
    __doc__ = WED.__doc__


class ARB(BodyMixin):
    """
    Arbitrary Convex Polyhedron

    :param name: of body
    :type name: str
    :param vertices: Eight vertices which make up the polyhedron as \
    [[x1, y1, z1], [x2, y2, z2], ...].  There must be eight even if \
    only six or seven vertices are needed to make up the polydedron.
    :type vertices: list
    :param facenumbers: The faces of the polyhedron expressed as floats \
    where each digit of the float refers to one of the vertices which makes \
    up that face. Six must always be provided as [1234,8765, ...], even if \
    only four or five faces are needed.  Any unneeded faces must be set to 0 \
    (no less than 4 sides).  Note that the references to the vertices are not \
    zero-counting.  The order of the vertices denoted in the facenumbers must \
    be either all clockwise or all anticlockwise, which if not obeyed
    will \ result in erroneous output without warning.
    :type facenumbers: float
    """
    def __init__(self, name, vertices, facenumbers, transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertices = [Three(v) for v in vertices]
        self.facenumbers = facenumbers

        self.transform = self._set_transform(transform)

        # Checking on the inputs to match FLUKA's behaviour described
        # in the manual.

        # Must always provide 8 vertices.
        if len(self.vertices) != 8:
            raise ValueError("8 vertices must always be supplied,"
                            " even if not all are used.")
        # Must always provide 6 facenumbers.
        if len(self.facenumbers) != 6:
            raise ValueError("6 face numbers must always be supplied,"
                            " even if not all are used.")

        self._nfaces = 6
        # Get the indices of the facenumbers equal to zero and count
        # how many faces we have by counting the number of zeros.
        zeros = [] # zero-counting index here to refer to face numbers...
        for i, facenumber in enumerate(self.facenumbers):
            if facenumber == 0:
                self._nfaces -= 1
                zeros.append(i)
        # Can't have less than 4 faces
        if self._nfaces < 4:
            raise ValueError("Not enough faces provided in arg facenumbers."
                            "  Must be 4, 5 or 6.")

        # Null-faces must be put as 0.0 in the facenumbers and they
        # must be at the end (i.e. 5 and 6 or 6).
        if zeros and (zeros != [4, 5] or zeros != [5]):
            raise ValueError("Facenumbers equal to zero to must be at"
                             " the end of the list.")

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return self.transform.leftMultiplyVector(Three([0, 0, 0]))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def _faceNumbersToZeroCountingIndices(self):
        # Convert the facenumbers which are one-indexed to
        # zero-indexed, and also account for the way in which faces
        # with 3 vertices are encoded.  Quotes from the FLUKA manual
        # are copied here to explain some of the logic.
        zeroCountingIndicesOut = []
        for fn in self.facenumbers:
            # "When the number of the faces is less than 6, the
            # remaining face description(s) must be zero, and must
            # appear at the end of the list."
            if fn == 0.0:
                continue
            fn = str(int(fn)) # Convert 1234.0 to string of integer 1234

            # "If a face has three vertices, the omitted position may
            # be either 0 or a repeat of one of the other vertices."
            fn = fn.replace("0", "")
            if len(set(fn)) != len(fn):
                unique_fn = []
                for n in fn:
                    if n not in unique_fn:
                        unique_fn.append(fn)
                fn = unique_fn

            # Finally we convert back to integers, subtract 1 to make
            # them zero-counding, and append to the list of outputted
            # zero counting indices.
            zeroCountingIndicesOut.append([int(n) - 1 for n in fn])

        return zeroCountingIndicesOut

    def _extent(self):
        vertices, _, _ = self._toVerticesAndPolygons(reverse=False)
        vertices = np.vstack(vertices)
        x = vertices[...,0]
        y = vertices[...,1]
        z = vertices[...,2]
        return _Extent([min(x), min(y), min(z)], [max(x), max(y), max(z)])

    def geant4Solid(self, greg, extent=None):
        verticesAndPolygons = self._getVerticesAndPolygons()
        return self._toTesselatedSolid(verticesAndPolygons,
                                       greg,
                                       addRegistry=True)

    def _toTesselatedSolid(self, verticesAndPolygons, greg, addRegistry):
        return g4.solid.TessellatedSolid(self.name,
                                         verticesAndPolygons,
                                         greg,
                                         addRegistry=addRegistry)

    def _getVerticesAndPolygons(self):
        extent = self._extent()
        verticesAndPolygons = self._toVerticesAndPolygons(reverse=False)
        # XXX: This is a fairly hacky but hopefully fairly robust way
        # to deal with arbitrary clockwise/anticlockwise vertex
        # ordering for the ARB input.
        g4reg = g4.Registry()
        tesselatedSolid = self._toTesselatedSolid(verticesAndPolygons,
                                                  g4reg,
                                                  addRegistry=False)
        envelopingBox = g4.solid.Box("test_box",
                                     10*(extent.size.x),
                                     10*(extent.size.y),
                                     10*(extent.size.z),
                                     g4reg,
                                     addRegistry=False)
        test_union = g4.solid.Union("test_union",
                                    tesselatedSolid,
                                    envelopingBox,
                                    [[0, 0, 0], [0, 0, 0]],
                                    g4reg,
                                    addRegistry=False)
        # If a null mesh results from a union, then the input mesh of
        # the ARB must have been malformed, as this is not otherwise possible.
        # Try reversing the vertex order, and return that either way.
        if not test_union.pycsgmesh().toPolygons():
            verticesAndPolygons = self._toVerticesAndPolygons(reverse=True)
        return verticesAndPolygons

    def _toVerticesAndPolygons(self, reverse):
        # Apply any expansion to the ARB's vertices.
        exp = self.transform.netExpansion()
        vertices = [exp * v for v in self.vertices]

        polygons = []
        for faceIndices in self._faceNumbersToZeroCountingIndices():
            faceVertices = [_geom.Vertex(vertices[i]) for i in faceIndices]
            if reverse:
                faceVertices = faceVertices[::-1]
            polygons.append(_geom.Polygon(faceVertices))

        return _CSG.fromPolygons(polygons).toVerticesAndPolygons()

    def __repr__(self):
        vs = map(list, self.vertices)
        vstrings = ["v{}={}".format(i, v) for (i, v)  in enumerate(vs, 1)]
        vstring = ", ".join(vstrings)
        return "<ARB: {}, {}, faces={}>".format(self.name,
                                                vstring, self.facenumbers)

    def _withLengthSafety(self, safety, reg):
        arb = ARB(self.name,
                  self.vertices,
                  self.facenumbers,
                  transform=self.transform,
                  flukaregistry=reg)
        vertices, faces , _ = arb._getVerticesAndPolygons()
        vertices = [np.array(v) for v in vertices]
        facenumbers = []
        for face in faces:
            faceVertices = [_geom.Vertex(vertices[i]) for i in face]
            polygon = _geom.Polygon(faceVertices)
            normal = polygon.plane.normal
            ls = safety * np.array(normal)
            for i in face:
                vertices[i] -= ls
            facenumbers.append([i+1 for i in face])

        # Convert lists of vertex integers for each face to individual floats
        facenumbersCorrected = []
        for fn in facenumbers:
            facenumbersCorrected.append(float("".join(str(f) for f in fn)))

        return ARB(self.name,
                   vertices,
                   facenumbersCorrected,
                   transform=self.transform,
                   flukaregistry=reg)


class XYP(_HalfSpaceMixin):
    """

    Infinite half-space delimited by the x-y plane (pependicular to the z-axis)

    :param name: of body
    :type name: str
    :param z: position of the x-y plane on the z-axis.  All points\
    less than z are considered to be part of this body.
    :type z: float

    """
    def __init__(self, name, z, transform=None, flukaregistry=None):
        self.name = name
        self.z = z

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        offset = self._extent_to_offset(extent)
        scale = self._extent_to_scale_factor(extent)
        return self.transform.leftMultiplyVector(Three(offset.x,
                                                       offset.y,
                                                       self.z - (scale * 0.5)))

    def __repr__(self):
        return "<XYP: {}, z={}>".format(self.name, self.z)

    def _withLengthSafety(self, safety, reg):
        return XYP(self.name,
                   self.z + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._halfspaceFreeStringHelper(self.z)


class XZP(_HalfSpaceMixin):
    """

    Infinite half-space delimited by the x-y plane (pependicular
    to the y-axis)

    :param name: of body
    :type name: str
    :param y: position of the x-y plane on the y-axis.  All points \
    less than y are considered to be part of this body.
    :type y: float

    """
    def __init__(self, name, y, transform=None, flukaregistry=None):
        self.name = name
        self.y = y

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        offset = self._extent_to_offset(extent)
        scale = self._extent_to_scale_factor(extent)
        return self.transform.leftMultiplyVector(Three(offset.x,
                                                       self.y - (scale * 0.5),
                                                       offset.z))

    def __repr__(self):
        return "<XZP: {}, y={}>".format(self.name, self.y)

    def _withLengthSafety(self, safety, reg):
        return XZP(self.name,
                   self.y + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._halfspaceFreeStringHelper(self.y)


class YZP(_HalfSpaceMixin):
    """

    Infinite half-space delimited by the x-y plane (pependicular to \
    the x-axis)

    :param name: of body
    :type name: str
    :param x: position of the x-y plane on the x-axis.  All points \
    less than x are considered to be part of this body.
    :type x: float

    """
    def __init__(self, name, x, transform=None, flukaregistry=None):
        self.name = name
        self.x = x

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        offset = self._extent_to_offset(extent)
        scale = self._extent_to_scale_factor(extent)
        return self.transform.leftMultiplyVector(Three(self.x - (scale * 0.5),
                                                       offset.y,
                                                       offset.z))

    def __repr__(self):
        return "<YZP: {}, x={}>".format(self.name, self.x)


    def _withLengthSafety(self, safety, reg):
        return YZP(self.name,
                   self.x + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._halfspaceFreeStringHelper(self.x)


class PLA(_HalfSpaceMixin):
    """
    Infinite half-space delimited by the x-y plane (pependicular to \
    the z-axis) Generic infinite half-space.

    :param name: of body
    :type name: str
    :param normal: position of a point on the plane
    :type point: list
    :param normal: vector perpendicular to the face of the plane, \
    pointing away from the contents of the half space.
    :type normal: list

    """
    def __init__(self, name, normal, point, transform=None, flukaregistry=None):
        self.name = name
        self.normal = Three(normal)
        self.point = Three(point)

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        offset = self._extent_to_offset(extent)
        # multiply by sqrt(3) to account for any rotation of the halfspace.
        scale = self._extent_to_scale_factor(extent)
        # Get point on plane closest to the centre of the extent:
        closest_point = self._closest_point(offset)
        return self.transform.leftMultiplyVector(closest_point
                                                 - 0.5
                                                 * scale * self.normal.unit())

    def _closest_point(self, point):
        """Get point on plane which is closest to point not on the plane."""
        distance = np.dot((self.point - point), self.normal.unit())
        closest_point = point + distance * self.normal.unit()
        return closest_point

    def rotation(self):
        # Choose the face pointing in the direction of the positive
        # z-axis to make the surface of the half space.
        return self.transform.leftMultiplyRotation(
            trans.matrix_from([0, 0, 1], self.normal))

    def __repr__(self):
        return "<PLA: {}, normal={}, point={}>".format(self.name,
                                                       list(self.normal),
                                                       list(self.point))

    def _withLengthSafety(self, safety, reg=None):
        norm = self.normal.unit()
        newpoint = self.point + norm * safety
        return PLA(self.name, norm, newpoint,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "PLA {} {}".format(self.name,
                                  _iterablesToFreeString(self.normal,
                                                            self.point))


class XCC(_InfiniteCylinderMixin):
    """Infinite Circular Cylinder parallel to the x-axis

    :param name: of body
    :type name: str
    :param y: position of the centre on the
    :type y: float
    :param z: position of the centre on the
    :type z: float
    :param radius: position of the centre on the
    :type radius: float

    """
    def __init__(self, name, y, z, radius, transform=None, flukaregistry=None):
        self.name = name
        self.y = y
        self.z = z
        self.radius = radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(extent_offset.x,
                                                       self.y,
                                                       self.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.array([[0, 0, -1],
                                                             [0, 1, 0],
                                                             [1, 0, 0]]))

    def __repr__(self):
        return "<XCC: {}, y={}, z={}>".format(self.name, self.y, self.z)

    def _withLengthSafety(self, safety, reg=None):
        return XCC(self.name, self.y, self.z, self.radius + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._infCylinderFreestringHelper(self.y, self.z)


class YCC(_InfiniteCylinderMixin):
    """Infinite Circular Cylinder parallel to the y-axis

    :param name: of body
    :type name: str
    :param z: position of the centre on the
    :type z: float
    :param x: position of the centre on the
    :type x: float
    :param radius: position of the centre on the
    :type radius: float

    """
    def __init__(self, name, z, x, radius, transform=None, flukaregistry=None):
        self.name = name
        self.z = z
        self.x = x
        self.radius = radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(self.x,
                                                       extent_offset.y,
                                                       self.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.array([[1, 0, 0],
                                                             [0, 0, 1],
                                                             [0, -1, 0]]))

    def __repr__(self):
        return "<YCC: {}, z={}, x={}>".format(self.name, self.z, self.x)

    def _withLengthSafety(self, safety, reg=None):
        return YCC(self.name, self.z, self.x, self.radius + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._infCylinderFreestringHelper(self.z, self.x)


class ZCC(_InfiniteCylinderMixin):
    """Infinite Circular Cylinder parallel to the z-axis

    :param name: of body
    :type name: str
    :param x: position of the centre on the
    :type x: float
    :param y: position of the centre on the
    :type y: float
    :param radius: position of the centre on the
    :type radius: float

    """
    def __init__(self, name, x, y, radius, transform=None, flukaregistry=None):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(self.x,
                                                       self.y,
                                                       extent_offset.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def __repr__(self):
        return "<ZCC: {}, x={}, y={}>".format(self.name, self.x, self.y)

    def _withLengthSafety(self, safety, reg=None):
        return ZCC(self.name, self.x, self.y, self.radius + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return self._infCylinderFreestringHelper(self.x, self.y, self.radius)


class XEC(BodyMixin):
    """Infinite Elliptical Cylinder parallel to the x-axis

    :param name: of body
    :type name: str
    :param y: position of the centre on the
    :type y: float
    :param z: position of the centre on the
    :type z: float
    :param ysemi: position of the centre on the
    :type ysemi: float
    :param zsemi: position of the centre on the
    :type zsemi: float

    """
    def __init__(self, name, y, z, ysemi, zsemi, transform=None, flukaregistry=None):
        self.name = name
        self.y = y
        self.z = z
        self.ysemi = ysemi
        self.zsemi = zsemi

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(extent_offset.x,
                                                       self.y,
                                                       self.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.array([[0, 0, -1],
                                                             [0, 1, 0],
                                                             [1, 0, 0]]))

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)
        return g4.solid.EllipticalTube(self.name,
                                       # full width, not semi:
                                       2 * exp * self.zsemi,
                                       2 * exp * self.ysemi,
                                       scale,
                                       reg,
                                       lunit="mm")

    def __repr__(self):
        return "<XEC: {}, y={}, z={}, ysemi={}, zsemi={}>".format(
            self.name,
            self.y, self.z,
            self.ysemi, self.zsemi)

    def _withLengthSafety(self, safety, reg=None):
        return XEC(self.name, self.y, self.z,
                   self.ysemi + safety,
                   self.zsemi + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "XEC {} {} {} {} {}".format(self.name,
                                           self.y, self.z,
                                           self.ysemi, self.zsemi)


class YEC(BodyMixin):
    """Infinite Elliptical Cylinder parallel to the y-axis

    :param name: of body
    :type name: str
    :param z: position of the centre on the
    :type z: float
    :param x: position of the centre on the
    :type x: float
    :param zsemi: position of the centre on the
    :type zsemi: float
    :param xsemi: position of the centre on the
    :type xsemi: float

    """
    def __init__(self, name, z, x, zsemi, xsemi, transform=None,
                 flukaregistry=None):
        self.name = name
        self.z = z
        self.x = x
        self.zsemi = zsemi
        self.xsemi = xsemi

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(self.x,
                                                       extent_offset.y,
                                                       self.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.array([[1, 0, 0],
                                                             [0, 0, 1],
                                                             [0, -1, 0]]))

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)
        return g4.solid.EllipticalTube(self.name,
                                       # full width, not semi
                                       2 * exp * self.xsemi,
                                       2 * exp * self.zsemi,
                                       scale,
                                       reg,
                                       lunit="mm")

    def __repr__(self):
        return "<YEC: {}, z={}, x={}, zsemi={}, xsemi={}>".format(
            self.name,
            self.z, self.x,
            self.zsemi, self.xsemi)

    def _withLengthSafety(self, safety, reg=None):
        return YEC(self.name, self.z, self.x,
                   self.zsemi + safety,
                   self.xsemi + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "YEC {} {} {} {} {}".format(self.name,
                                           self.z, self.x,
                                           self.zsemi, self.xsemi)


class ZEC(BodyMixin):
    """Infinite Elliptical Cylinder parallel to the z-axis

    :param name: of body
    :type name: str
    :param x: position of the centre on the
    :type x: float
    :param y: position of the centre on the
    :type y: float
    :param xsemi: position of the centre on the
    :type xsemi: float
    :param ysemi: position of the centre on the
    :type ysemi: float

    """
    def __init__(self, name, x, y, xsemi, ysemi, transform=None,
                 flukaregistry=None):
        self.name = name
        self.x = x
        self.y = y
        self.xsemi = xsemi
        self.ysemi = ysemi

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        extent_offset = self._extent_to_offset(extent)
        return self.transform.leftMultiplyVector(Three(self.x,
                                                       self.y,
                                                       extent_offset.z))

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)
        return g4.solid.EllipticalTube(self.name,
                                       # full width, not semi
                                       2 * exp * self.xsemi,
                                       2 * exp * self.ysemi,
                                       scale,
                                       reg,
                                       lunit="mm")

    def __repr__(self):
        return "<ZEC: {}, x={}, y={}, xsemi={}, ysemi={}>".format(
            self.name,
            self.x, self.y,
            self.xsemi, self.ysemi)

    def _withLengthSafety(self, safety, reg=None):
        return ZEC(self.name, self.x, self.y,
                   self.xsemi + safety,
                   self.ysemi + safety,
                   transform=self.transform,
                   flukaregistry=reg)

    def flukaFreeString(self):
        return "ZEC {} {} {} {} {}".format(self.name,
                                           self.x, self.y,
                                           self.xsemi, self.ysemi)

class QUA(BodyMixin):
    """Generic quadric

    :param name: of body
    :type name: str
    :param Axx: x^2 coefficient
    :type Axx: float
    :param Ayy: y^2 coefficient
    :type Ayy: float
    :param Azz: z^2 coefficient
    :type Azz: float
    :param Axy: xy coefficient
    :type Axy: float
    :param Axz: xz coefficient
    :type Axz: float
    :param Ayz: yz coefficient
    :type Ayz: float
    :param Ax : x coefficient
    :type Ax: float
    :param Ay : y coefficient
    :type Ay: float
    :param Az : z coefficient
    :type Az: float
    :param A0 : constant
    :type A0: constant
    """
    def __init__(self, name,
                 Axx, Ayy, Azz, Axy, Axz, Ayz, Ax, Ay, Az, A0,
                 transform=None,
                 flukaregistry=None):
        self.name = name

        self.Axx = Axx
        self.Ayy = Ayy
        self.Azz = Azz
        self.Axy = Axy
        self.Axz = Axz
        self.Ayz = Ayz
        self.Ax  = Ax
        self.Ay  = Ay
        self.Az  = Az
        self.A0  = A0

        self.transform = self._set_transform(transform)

        self.addToRegistry(flukaregistry)

    def centre(self, extent=None):
        return Three([0,0,0])

    def rotation(self):
        return self.transform.leftMultiplyRotation(np.identity(3))

    def geant4Solid(self, reg, extent=None):
        exp = self.transform.netExpansion()
        scale = self._extent_to_scale_factor(extent)

        quadric = vtk.vtkQuadric()
        quadric.SetCoefficients(self.Axx, self.Ayy, self.Azz,
                                self.Axy, self.Ayz, self.Axz,
                                self.Ax,  self.Ay,  self.Az, 0.0)
        sample = vtk.vtkSampleFunction()
        sample.SetSampleDimensions(50, 50, 50)
        sample.SetModelBounds(-1,1,-1,1,-1,1)
        sample.SetImplicitFunction(quadric)
        sample.SetCapping(1)

        contours = vtk.vtkContourFilter()
        contours.SetInputConnection(sample.GetOutputPort())
        contours.GenerateValues(1, -self.A0, -self.A0)
        contours.Update()

        pd = contours.GetOutput()

        mesh  = []
        verts = []
        facet = []

        for i in range(pd.GetNumberOfCells()) :
            c = pd.GetCell(i)
            p = c.GetPoints()
            verts.append(np.array(p.GetPoint(2)))
            verts.append(np.array(p.GetPoint(1)))
            verts.append(np.array(p.GetPoint(0)))
            facet.append([3*i+0,3*i+1,3*i+2])

        mesh.append(verts)
        mesh.append(facet)

        return g4.solid.TessellatedSolid(
            self.name,
            mesh,
            reg,
            g4.solid.TessellatedSolid.MeshType.Freecad)

    def _withLengthSafety(self, safety, reg=None):
        return QUA(self.name,
                   self.Axx, self.Ayy, self.Azz,
                   self.Axy, self.Axz, self.Ayz,
                   self.Ax, self.Ay,  self.Az, self.A0,
                   transform=self.transform,
                   flukaregistry=reg)

def _raiseIfNotAllMutuallyPerpendicular(first, second, third, message):
    if (first.dot(second) != 0.0
            or first.dot(third) != 0
            or second.dot(third) != 0.0):
        raise ValueError(message)

def _iterablesToFreeString(*iterables):
    return " ".join([str(e) for e in chain(*iterables)])
