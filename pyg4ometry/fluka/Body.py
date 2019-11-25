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

INFINITY = 500

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



class RPP(Body):
    """
    An RPP is a rectangular parallelpiped (a cuboid)

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
                 expansion=1.0,
                 translation=[0,0,0],
                 rotdefi=None,
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
        return self.lower + 0.5 * self.upper

    def rotation(self):
        return _np.identity(3)

    def geant4_solid(self, reg, scale=None):
        self.g4_solid =  _g4.solid.Box(self.name,
                                       self.upper[0]-self.lower[0],
                                       self.upper[1]-self.lower[1],
                                       self.upper[2]-self.lower[2],
                                       reg,
                                       lunit="mm")
        return self.g4_solid

    def __repr__(self):
        l = self.lower
        u = self.upper
        return ("<RPP: {},"
                " x0={l.x}, x1={u.x},"
                " y0={l.y}, y1={u.y},"
                " z0={l.z}, z1={u.z}>").format(self.name, l=l, u=u)

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

    def geant4_solid(self, greg, scale=None):
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


class _WED_RAW(Body):
    """WED and RAW are aliases for one another, so we define it in a
    single place and then inherit this class to provide the correct
    names below.

    """
    def __init__(self, name, vertex, edge1, edge2, edge3, flukaregistry):
        self.name = name
        self.vertex = _Three(vertex)
        self.edge1 = _Three(edge1)  # direction of the triangular face.
        self.edge2 = _Three(edge2)  # direction of length of the prism.
        self.edge3 = _Three(edge3)  # other direction of the triangular face.
        # from IPython import embed; embed()
        _raise_if_not_all_mutually_perpendicular(
            self.edge1, self.edge2, self.edge3,
            "Edges are not all mutually perpendicular")

    def centre(self):
        return self.vertex

    def rotation(self):
        initial1 = [1, 0, 0] # self.edge1 starts off pointing in the x-direction
        initial2 = [0, 0, 1] # self.edge2 starts off pointing in the z-direction
        initial3 = [0, 1, 0] # self.edge3 starts off pointing in the y-direction

        # return _trans.three_fold_orientation(initial1,
        #                                      self.edge1,
        #                                      initial2,
        #                                      self.edge2,
        #                                      initial3,
        #                                      self.edge3).T
        basis1 = _np.array([initial1,
                            initial2,
                            initial3])
        basis2 = _np.array([self.edge1.unit(),
                            self.edge2.unit(),
                            self.edge3.unit()])
        # from IPython import embed; embed()
        return basis1.T.dot(basis2)


        # return _trans.two_fold_orientation(initial1,
        #                                      self.edge1,
        #                                      initial2,
        #                                      self.edge2
        #                                      # initial3,
        #                                      # self.edge3
        # ).T


    def geant4_solid(self, greg, scale=None):
        # We choose self.vertex to be at [0, 0].
        face = [[0, 0],
                [self.edge1.length(), 0],
                [0, self.edge3.length()]]
        return _g4.solid.ExtrudedSolid(self.name,
                                       face,
                                       [[0,[0, 0], 1],
                                        [self.edge2.length(), [0, 0], 1]],
                                       registry=greg)



class WED(_WED_RAW):
    pass


class RAW(_WED_RAW):
    pass


class ARB(Body):
    """ Has 4, 5, or 6 faces.

    vertices: 8 vertices must be provided as a list of 8 lists,
    i.e. [[x1, y1, z1], [x2, y2, y2], ...].
    facenumbers: a list of 4 numbers which refers to the vertices
    making up the six faces.  The vertex numbers must be provided
    either ALL in clockwise order or ALL in anticlockwise order.
    Combining the two conventions will result in erroneous output
    without warning.

    """

    def __init__(self, name, vertices, facenumbers, flukaregistry):
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

    def geant4_solid(self, reg, scale=None):
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

    def geant4_solid(self, reg, scale=None):
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

    def geant4_solid(self, registry, scale=None):
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
    def geant4_solid(self, registry, scale=None):
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

    def geant4_solid(self, reg, scale=None):
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
