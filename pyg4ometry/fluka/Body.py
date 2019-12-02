import numpy as _np
from Vector import Three as _Three
import pyg4ometry.pycsg.core
from pyg4ometry.pycsg.core import CSG as _CSG
import pyg4ometry.pycsg.geom as _geom


import pyg4ometry.transformation as _trans
import pyg4ometry.geant4 as _g4

import logging
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

INFINITY = 50000
LENGTH_SAFETY = 1e-6


class Body(object):
    """
    Base class representing a body as defined in FLUKA
    """

    def __init__(self):
        pass

    def addToRegistry(self, flukaregistry):
        if flukaregistry is not None:
            flukaregistry.addBody(self)

    def tbxyz(self):
        return _trans.matrix2tbxyz(self.rotation())

    # in the per body _with_lengthsafety methods below, factor =
    # -1*LENGTH_SAFETY should make the body small in
    # _with_lengthsafety, and +LENGTH_SAFETY must make the body
    # bigger.
    def safety_expanded(self, reg=None):
        return self._with_lengthsafety(LENGTH_SAFETY, reg)

    def safety_shrunk(self, reg=None):
        return self._with_lengthsafety(-LENGTH_SAFETY, reg)


class _HalfSpace(Body):
    # Base class for XYP, XZP, YZP.
    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, registry, scale=None):
        return _g4.solid.Box(self.name,
                             INFINITY,
                             INFINITY,
                             INFINITY,
                             registry)


class _InfiniteCylinder(Body):
    # Base class for XCC, YCC, ZCC.
    def geant4_solid(self, registry, scale=None):
        return _g4.solid.Tubs(self.name,
                              0.0,
                              self.radius,
                              INFINITY,
                              0.0, 2*_np.pi,
                              registry,
                              lunit="mm")


class RPP(Body):
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
                 xmin, xmax,
                 ymin, ymax,
                 zmin, zmax,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name  = name
        self.lower = _Three([xmin, ymin, zmin])
        self.upper = _Three([xmax, ymax, zmax])

        if not all([xmin < xmax, ymin < ymax, zmin < zmax]):
            raise ValueError("Each of the xmin, ymin, zmin must be"
                             " smaller than the corresponding"
                             " xmax, ymax, zmax.")


        self.addToRegistry(flukaregistry)

    def centre(self):
        return 0.5 * (self.lower + self.upper)

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, reg, scale=None):
        v = self.upper - self.lower
        return  _g4.solid.Box(self.name,
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

    def _with_lengthsafety(self, safety, reg):
        lower = self.lower - [safety, safety, safety]
        upper = self.upper + [safety, safety, safety]
        return RPP(self.name,
                   lower.x, upper.x,
                   lower.y, upper.y,
                   lower.z, upper.z,
                   flukaregistry=reg)



class BOX(Body):
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
    def __init__(self, name, vertex, edge1, edge2, edge3,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertex = _Three(vertex)
        self.edge1 = _Three(edge1)
        self.edge2 = _Three(edge2)
        self.edge3 = _Three(edge3)

        _raise_if_not_all_mutually_perpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutally orthogonal.")

    def centre(self):
        return self.vertex + 0.5 * (self.edge1 + self.edge2 + self.edge3)

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, greg, scale=None):
        return _g4.solid.Box(self.name,
                             self.edge1.length(),
                             self.edge2.length(),
                             self.edge3.length(),
                             greg,
                             lunit="mm")

    def __repr__(self):
        return ("<BOX: {}, v={}, e1={}, e2={}, e3={}, >").format(
            self.name,
            list(self.vertex),
            list(self.edge1), list(self.edge2), list(self.edge3))


class SPH(Body):
    """Sphere

    :param name: of body
    :type name: str
    :param point: position [x, y, z] of the centre of the sphere.
    :type point: list
    :param radius: radius of the sphere.
    :type radius: float

    """
    def __init__(self, name, point, radius,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
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

    def geant4_solid(self, reg, scale=None):
        return _g4.solid.Orb(self.name,
                             self.radius,
                             reg,
                             lunit="mm")

    def __repr__(self):
        return "<SPH: {}, centre={}, r={})>".format(self.name,
                                                    list(self.centre()),
                                                    self.radius)

    def _with_lengthsafety(self, safety, reg):
        return SPH(self.name, self.point, self.radius + safety,
                   flukaregistry=reg)


class RCC(Body):
    """Right Circular Cylinder

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the faces of the cylinder.
    :type vertex: list
    :param edge1: vector [x, y, z] denoting the direction along the
    length of the cylinder.
    :type edge1: list
    :param edge2: radius of the cylinder face.
    :type edge2: float

    """
    def __init__(self, name, face, direction, radius,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
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

    def geant4_solid(self, reg, scale=None):
        return _g4.solid.Tubs(self.name,
                              0.0,
                              self.radius,
                              self.direction.length(),
                              0.0,
                              2*_np.pi,
                              reg,
                              lunit="mm")

    def __repr__(self):
        return ("<RCC: {}, face={}, dir={}, r={}>").format(
            self.name, list(self.face), list(self.direction), self.radius)

    def _with_lengthsafety(self, safety, reg):
        unit = self.direction.unit()
        face = self.face - safety * unit
        direction = self.direction + safety * unit
        return RCC(self.name,
                   face, direction,
                   self.radius + safety,
                   flukaregistry=reg)


class REC(Body):
    """Right Elliptical Cylinder

    :param name: of body
    :type name: str
    :param vertex: position [x, y, z] of one of the faces of the cylinder.
    :type vertex: list
    :param semiminor: vector [x, y, z] denoting the direction along the
    semiminor axis of the ellipse.
    :type semiminor: list
    :param semimajor: vector [x, y, z] denoting the direction along the
    semimajor axis of the ellipse.
    :type semimajor: list

    """
    def __init__(self, name, face, direction, semiminor, semimajor,
                 expansion=None,
                 translation=None,
                 transform=None,
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

    def geant4_solid(self, reg, scale=None):
        return _g4.solid.EllipticalTube(self.name,
                                        2 * self.semiminor.length(),
                                        2 * self.semimajor.length(),
                                        self.direction.length(),
                                        reg,
                                        lunit="mm")

    def __repr__(self):
        return ("<REC: {}, face={}, dir={}, semimin={}, semimaj={}>").format(
            self.name,
            list(self.face), list(self.direction),
            list(self.semiminor), list(self.semimajor))


class TRC(Body):
    """Truncated Right-angled Cone

    :param name: of body
    :type name: str
    :param major_centre: vector [x, y, z] position of the centre of the
    larger face.
    :type major_centre: list
    :param direction: vector [x, y, z] pointing from the larger face
    to the smaller face.
    :type direction: list
    :param major_radius: radius of the larger face.
    :type major_radius: float
    :param minor_radius: radius of the smaller face.
    :type minor_radius: float

    """
    def __init__(self, name, major_centre, direction,
                 major_radius, minor_radius,
                 expansion=None,
                 translation=None,
                 transform=None,
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

    def geant4_solid(self, registry, scale=None):
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
        return ("<TRC: {}, major={} direction={} rmaj={}, rmin={}>").format(
            self.name,
            list(self.major_centre),
            list(self.direction),
            self.major_radius,
            self.minor_radius)


class ELL(Body):
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
    def __init__(self, name, focus1, focus2, length,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
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

    def geant4_solid(self, greg, scale=None):
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

    def __repr__(self):
        return "<ELL: {}, f1={}, f2={}, length={}>".format(
            self.name, list(self.focus1), list(self.focus2), self.length)


class _WED_RAW(Body):
    # WED and RAW are aliases for one another, so we define it in a
    # single place and then inherit this class to provide the correct
    # type names below.
    def __init__(self, name, vertex, edge1, edge2, edge3,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertex = _Three(vertex)
        self.edge1 = _Three(edge1)  # direction of the triangular face.
        self.edge2 = _Three(edge2)  # direction of length of the prism.
        self.edge3 = _Three(edge3)  # other direction of the triangular face.
        _raise_if_not_all_mutually_perpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutually perpendicular.")
        self.addToRegistry(flukaregistry)

    def centre(self):
        # need to determine the handedness of the three direction
        # vectors to get the correct vertex to use.
        crossproduct = _np.cross(self.edge1, self.edge3)
        if _trans.are_parallel(crossproduct, self.edge2):
            return self.vertex
        elif _trans.are_anti_parallel(crossproduct, self.edge2):
            return self.vertex + self.edge2
        else:
            raise ValueError(
                "Unable to determine if parallel or anti-parallel.")

    def rotation(self):
        initial1 = [1, 0, 0] # edge1 starts off pointing in the x-direction.
        initial3 = [0, 1, 0] # edge3 starts off pointing in the y-direction.
        return _trans.two_fold_orientation(initial1, self.edge1.unit(),
                                           initial3, self.edge3.unit())

    def geant4_solid(self, greg, scale=None):
        face = [[0, 0],
                [self.edge1.length(), 0],
                [0, self.edge3.length()]]

        return _g4.solid.ExtrudedSolid(self.name,
                                       face,
                                       [[0,[0, 0], 1],
                                        [self.edge2.length(), [0, 0], 1]],
                                       registry=greg)

    def __repr__(self):
        return ("<{}: {}, v={}, e1={}, e2={}, e3={}>").format(
            type(self).__name__, # Can be either WED or RAW
            self.name,
            list(self.vertex),
            list(self.edge1),
            list(self.edge2),
            list(self.edge3))


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


class ARB(Body):
    """Arbitrary Convex Polyhedron

    :param name: of body
    :type name: str
    :param vertices: Eight vertices which make up the polyhedron as
    [[x1, y1, z1], [x2, y2, z2], ...].  There must be eight even if
    only six or seven vertices are needed to make up the polydedron.
    :type vertices: list
    :param facenumbers: The faces of the polyhedron expressed as
    floats where each digit of the float refers to one of the vertices
    which makes up that face. Six must always be provided as [1234,
    8765, ...], even if only four or five faces are needed.  Any
    unneeded faces must be set to 0 (no less than 4 sides).  Note that
    the references to the vertices are not zero-counting.  The order
    of the vertices denoted in the facenumbers must be either all
    clockwise or anticlockwise, which if not obeyed will result in
    erroneous output without warning.
    """
    def __init__(self, name, vertices, facenumbers,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.vertices = [_Three(v) for v in vertices]
        self.facenumbers = facenumbers

        if len(self.vertices) != 8:
            raise TypeError("8 vertices must always be supplied,"
                            " even if not all are used.")
        if len(self.facenumbers) != 6:
            raise TypeError("6 face numbers must always be supplied.")

        self._nfaces = 6
        for facenumber in self.facenumbers:
            if facenumber == 0:
                self._nfaces -= 1
        if self._nfaces < 4:
            raise TypeError("Not enough faces provided in arg facenumbers."
                            "  Must be 4, 5 or 6.")
        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(0, 0, 0)

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, greg, scale=None):
        # pyg4ometry expects right handed corkscrew for the vertices
        # for TesselatedSolid (and in general).
        # Fluka however for ARB can take either all right or left
        # handed (but no mixing and matching).  If our normals are all in
        # the wrong direction, when we union with a solid which
        # envelops that tesselated solid we will get a NullMeshError,
        # which we can catch and then we invert the mesh and return
        # that TesselatedSolid.

        # We need the minimum and maximum extents of the tesselated
        # solid to make the enveloping box.
        xmin = 0
        xmax = 0
        ymin = 0
        ymax = 0
        zmin = 0
        zmax = 0
        polygon_list = []
        for fnumber in self.facenumbers:
            if fnumber == 0:
                continue

            # store the digits of the fnumbers as indices which are
            # zero counting (c.f. input in which they count from 1)
            zc_vertex_indices = []

            for vertex_index in str(int(fnumber)):
                zero_counting_index = int(vertex_index) - 1
                 # duplicate digits in the fnumber should be ignored
                if zero_counting_index in zc_vertex_indices:
                    continue
                # digit=0 in the fnumber should be ignored, no extra vertex
                if zero_counting_index == -1:
                    continue
                zc_vertex_indices.append(zero_counting_index)

                xmin = min(xmin, self.vertices[zero_counting_index].x)
                xmax = max(xmax, self.vertices[zero_counting_index].x)
                ymin = min(ymin, self.vertices[zero_counting_index].y)
                ymax = max(ymax, self.vertices[zero_counting_index].y)
                zmin = min(zmin, self.vertices[zero_counting_index].z)
                zmax = max(zmax, self.vertices[zero_counting_index].z)


            face_vertices = [_geom.Vertex(self.vertices[i])
                             for i in zc_vertex_indices]
            polygon = _geom.Polygon(face_vertices)
            polygon_list.append(polygon)

        mesh = _CSG.fromPolygons(polygon_list)
        vertices_and_polygons = mesh.toVerticesAndPolygons()
        tesselated_solid = _g4.solid.TessellatedSolid(self.name,
                                                      vertices_and_polygons,
                                                      greg,
                                                      addRegistry=False)
        # make massive box with totally envelops the tesselated solid
        big_box = _g4.solid.Box("test_box",
                                10*(xmax - xmin),
                                10*(ymax - ymin),
                                10*(zmax - zmin),
                                greg,
                                addRegistry=False)
        test_union = _g4.solid.Union("test_union",
                                     tesselated_solid,
                                     big_box,
                                     [[0,0,0],[0,0,0]],
                                     _g4.Registry(),
                                     addRegistry=False)
        try:
            # try to mesh the union of the enveloping box and the
            # tesselated solid.  if we get a null mesh error we have
            # the faces the wrong way around.
            test_union.pycsgmesh()
        except pyg4ometry.exceptions.NullMeshError:
            # inverse to get it right
            vertices_and_polygons = mesh.inverse().toVerticesAndPolygons()
        return _g4.solid.TessellatedSolid(self.name,
                                          vertices_and_polygons,
                                          greg)

    def __repr__(self):
        vs = map(list, self.vertices)
        vstrings = ["v{}={}".format(i, v) for (i, v)  in enumerate(vs, 1)]
        vstring = ", ".join(vstrings)
        return "<ARB: {}, {}, faces={}>".format(self.name,
                                                vstring, self.facenumbers)


class XYP(_HalfSpace):
    """Infinite half-space delimited by the x-y plane (pependicular to
    the z-axis)

    :param name: of body
    :type name: str
    :param z: position of the x-y plane on the z-axis.  All points
    less than z are considered to be part of this body.
    :type z: float

    """
    def __init__(self, name, z,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.z = z
        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre =  transverseOffset + _Three(0, 0, self.z - (INFINITY * 0.5))
        return centre

    def __repr__(self):
        return "<XYP: {}, z={}>".format(self.name, self.z)

    def _with_lengthsafety(self, safety, reg):
        return XYP(self.name,
                   self.z + safety,
                   flukaregistry=reg)


class XZP(_HalfSpace):
    """Infinite half-space delimited by the x-y plane (pependicular to
    the y-axis)

    :param name: of body
    :type name: str
    :param y: position of the x-y plane on the y-axis.  All points
    less than y are considered to be part of this body.
    :type y: float
    """
    def __init__(self, name, y,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.y = y
        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre = transverseOffset + _Three(0, self.y - (INFINITY * 0.5), 0)
        return centre

    def __repr__(self):
        return "<XZP: {}, y={}>".format(self.name, self.y)

    def _with_lengthsafety(self, safety, reg):
        return XZP(self.name,
                   self.y + safety,
                   flukaregistry=reg)


class YZP(_HalfSpace):
    """Infinite half-space delimited by the x-y plane (pependicular to
    the x-axis)

    :param name: of body
    :type name: str
    :param x: position of the x-y plane on the x-axis.  All points
    less than x are considered to be part of this body.
    :type x: float

    """
    def __init__(self, name, x,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.x = x
        self.addToRegistry(flukaregistry)

    def centre(self):
        transverseOffset = _Three(0, 0 ,0)
        centre = transverseOffset + _Three(self.x - (INFINITY * 0.5), 0, 0)
        return centre

    def __repr__(self):
        return "<YZP: {}, x={}>".format(self.name, self.x)


    def _with_lengthsafety(self, safety, reg):
        return YZP(self.name,
                   self.x + safety,
                   flukaregistry=reg)


class PLA(Body):
    """Infinite half-space delimited by the x-y plane (pependicular to
    the z-axis)

    :param name: of body
    :type name: str
    :param normal: position of a point on the plane
    :type point: list
    :param normal: vector perpendicular to the face of the plane,
    pointing away from the contents of the half space.
    :type normal: list
    """
    def __init__(self, name, normal, point,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.normal = _Three(normal)
        self.point = _Three(point)

        # normalise it if it is not normalised.
        self.normal = self.normal / _np.linalg.norm(self.normal)

        self.addToRegistry(flukaregistry)

    def centre(self):
        return self.point - 0.5 * INFINITY * self.normal.unit()

    def rotation(self):
        # Choose the face pointing in the direction of the positive
        # z-axis to make the surface of the half space.
        return _trans.matrix_from([0, 0, 1], self.normal)

    def geant4_solid(self, reg, scale=None):
        return _g4.solid.Box(self.name,
                             INFINITY,
                             INFINITY,
                             INFINITY,
                             reg,
                             lunit="mm")

    def __repr__(self):
        return "<PLA: {}, normal={}, point={}>".format(self.name,
                                                       list(self.normal),
                                                       list(self.point))


class XCC(_InfiniteCylinder):
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
    def __init__(self, name, y, z, radius,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.y = y
        self.z = z
        self.radius = radius

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(0.0, self.y, self.z)

    def rotation(self):
        return _np.array([[0, 0, -1],
                          [0, 1, 0],
                          [1, 0, 0]])

    def __repr__(self):
        return "<XCC: {}, y={}, z={}>".format(self.name, self.y, self.z)

    def _with_lengthsafety(self, safety, reg=None):
        return XCC(self.name, self.y, self.z, self.radius + safety,
                   flukaregistry=reg)


class YCC(_InfiniteCylinder):
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
    def __init__(self, name, z, x, radius,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.z = z
        self.x = x
        self.radius = radius

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(self.x, 0.0, self.z)

    def rotation(self):
        return _np.array([[1, 0, 0],
                          [0, 0, 1],
                          [0, -1, 0]])

    def __repr__(self):
        return "<YCC: {}, z={}, x={}>".format(self.name, self.z, self.x)

    def _with_lengthsafety(self, safety, reg=None):
        return YCC(self.name, self.z, self.x, self.radius + safety,
                   flukaregistry=reg)


class ZCC(_InfiniteCylinder):
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
    def __init__(self, name, x, y, radius,
                 expansion=None,
                 translation=None,
                 transform=None,
                 flukaregistry=None):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius

        self.addToRegistry(flukaregistry)

    def centre(self):
        return _Three(self.x, self.y, 0.0)

    def rotation(self):
        return _np.identity(3)

    def __repr__(self):
        return "<ZCC: {}, x={}, y={}>".format(self.name, self.x, self.y)

    def _with_lengthsafety(self, safety, reg=None):
        return ZCC(self.name, self.x, self.y, self.radius + safety,
                   flukaregistry=reg)


class XEC(Body):
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
    def __init__(self, name, y, z, ysemi, zsemi,
                 expansion=None,
                 translation=None,
                 transform=None,
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

    def geant4_solid(self, reg, scale=None):
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

    def _with_lengthsafety(self, safety, reg=None):
        return XEC(self.name, self.y, self.z,
                   self.ysemi + safety,
                   self.zsemi + safety,
                   flukaregistry=reg)


class YEC(Body):
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
    def __init__(self, name, z, x, zsemi, xsemi,
                 expansion=None,
                 translation=None,
                 transform=None,
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

    def geant4_solid(self, reg, scale=None):
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

    def _with_lengthsafety(self, safety, reg=None):
        return YEC(self.name, self.z, self.x,
                   self.zsemi + safety,
                   self.xsemi + safety,
                   flukaregistry=reg)


class ZEC(Body):
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
    def __init__(self, name, x, y, xsemi, ysemi,
                 expansion=None,
                 translation=None,
                 transform=None,
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

    def geant4_solid(self, reg, scale=None):
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

    def _with_lengthsafety(self, safety, reg=None):
        return ZEC(self.name, self.x, self.y,
                   self.xsemi + safety,
                   self.ysemi + safety,
                   flukaregistry=reg)


def _raise_if_not_all_mutually_perpendicular(first, second, third, message):
    if (first.dot(second) != 0.0
        or first.dot(third) != 0
        or second.dot(third) != 0.0):
        raise ValueError(message)
