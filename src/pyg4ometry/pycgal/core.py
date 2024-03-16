from . import CGAL
from . import Surface_mesh
from . import Polygon_mesh_processing
from . import geom
from . import Aff_transformation_3
from . import Vector_3
from . import Point_2
from . import Partition_traits_2_Polygon_2
from . import Polygon_2
from . import Polygon_with_holes_2
from . import Polyhedron_3
from . import Triangle_3
from . import Vector_3
from . import CGAL
from . import pythonHelpers

import numpy as _np


class CSG:
    def __init__(self):
        self.sm = Surface_mesh.Surface_mesh_EPECK()

    @classmethod
    def fromPolygons(cls, polygons, **kwargs):
        csg = CSG()
        csg.sm = Surface_mesh.Surface_mesh_EPECK()
        Surface_mesh.toCGALSurfaceMesh(csg.sm, polygons)
        Polygon_mesh_processing.triangulate_faces(csg.sm)
        return csg

    def toVerticesAndPolygons(self):
        return Surface_mesh.toVerticesAndPolygons(self.sm)

    def clone(self):
        csg = CSG()
        csg.sm = self.sm.clone()
        return csg

    def rotate(self, axisIn, angleDeg):
        rot = _np.zeros((3, 3))

        axis = geom.Vector(axisIn)

        normAxis = axis / axis.length()

        cosAngle = _np.cos(-angleDeg / 180.0 * _np.pi)
        sinAngle = _np.sin(-angleDeg / 180.0 * _np.pi)
        verSin = 1 - cosAngle

        x = normAxis.x
        y = normAxis.y
        z = normAxis.z

        rot[0][0] = (verSin * x * x) + cosAngle
        rot[0][1] = (verSin * x * y) - (z * sinAngle)
        rot[0][2] = (verSin * x * z) + (y * sinAngle)

        rot[1][0] = (verSin * y * x) + (z * sinAngle)
        rot[1][1] = (verSin * y * y) + cosAngle
        rot[1][2] = (verSin * y * z) - (x * sinAngle)

        rot[2][0] = (verSin * z * x) - (y * sinAngle)
        rot[2][1] = (verSin * z * y) + (x * sinAngle)
        rot[2][2] = (verSin * z * z) + cosAngle

        rotn = Aff_transformation_3.Aff_transformation_3_EPECK(
            rot[0][0],
            rot[0][1],
            rot[0][2],
            rot[1][0],
            rot[1][1],
            rot[1][2],
            rot[2][0],
            rot[2][1],
            rot[2][2],
            1,
        )
        Polygon_mesh_processing.transform(rotn, self.sm)

    def translate(self, disp):
        vIn = geom.Vector(disp)
        # TODO tidy vector usage (i.e conversion in geom?)
        v = Vector_3.Vector_3_EPECK(vIn[0], vIn[1], vIn[2])
        transl = Aff_transformation_3.Aff_transformation_3_EPECK(CGAL.Translation(), v)
        Polygon_mesh_processing.transform(transl, self.sm)

    # TODO need to finish and check signatures
    def scale(self, *args):
        if len(args) == 3:  # x,y,z
            x = args[0]
            y = args[1]
            z = args[2]
        elif len(args) == 1:
            if type(args[0]) is list:
                x = args[0][0]
                y = args[0][1]
                z = args[0][2]
            else:  # Vector
                x = args[0][0]
                y = args[0][1]
                z = args[0][2]
        else:
            x = 1
            y = 1
            z = 1
        scal = Aff_transformation_3.Aff_transformation_3_EPECK(x, 0, 0, 0, y, 0, 0, 0, z, 1)
        Polygon_mesh_processing.transform(scal, self.sm)

    def getNumberVertices(self):
        return self.sm.number_of_vertices()

    def getNumberPolys(self):
        return self.sm.number_of_faces()

    def vertexCount(self):
        return self.sm.number_of_vertices()

    def polygonCount(self):
        return self.sm.number_of_faces()

    def intersect(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_intersection(self.sm, csg2.sm, out)
        csg = CSG()
        csg.sm = out
        return csg

    def union(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_union(self.sm, csg2.sm, out)
        csg = CSG()
        csg.sm = out
        return csg

    def subtract(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_difference(self.sm, csg2.sm, out)
        csg = CSG()
        csg.sm = out
        return csg

    def inverse(self):
        CGAL.reverse_face_orientations(self.sm)
        return self

    # TODO finish coplanar intersection
    def coplanarIntersection(self, csg):
        """
        Compute the coplanar surfaces between self and csg

        """

        sm1 = self.sm
        sm2 = csg.sm

        #######################################
        # triangle planes
        #######################################

        def makePlaneList(sm):
            # triangle plane list
            tplanel = []

            # loop over sm1 faces and make planes
            for f in sm.faces():
                he = Surface_mesh.Halfedge_index()
                sm.halfedge(f, he)

                tpl = []

                for he1 in CGAL.halfedges_around_face(he, sm):
                    vi = sm.source(he1)
                    p = sm.point(vi)
                    tpl.append(p)

                t = Triangle_3.Triangle_3_EPECK(tpl[0], tpl[1], tpl[2])
                if t.is_degenerate():
                    print("degenerate triangle")

                pl = t.supporting_plane()
                tplanel.append([pl, t])

            return tplanel

        #######################################
        # Are two planes close?
        #######################################
        def close(p1, p2):
            p1dir = p1[0].orthogonal_direction()
            p1poi = p1[0].point()

            p2dir = p2[0].orthogonal_direction()
            p2poi = p2[0].point()

            # print(p1dir,p2dir,p1poi,p2poi)
            pd0 = Vector_3.Vector_3_EPECK(p2poi, p1poi)
            dd0 = p2dir.vector() - p1dir.vector()
            dd1 = p2dir.vector() + p1dir.vector()

            if CGAL.to_double(pd0.squared_length()) < 0.0001 and (
                CGAL.to_double(dd0.squared_length()) < 0.0001
                or CGAL.to_double(dd1.squared_length()) < 0.0001
            ):
                return True
            else:
                return False

        tpl1 = makePlaneList(sm1)
        tpl2 = makePlaneList(sm2)

        # return surface mesh
        c = CSG()
        out = c.sm

        # close planes
        for tpl1i in tpl1:
            for tpl2i in tpl2:
                # check if planes are close
                bClose = close(tpl1i, tpl2i)

                # if close compute 2d intersection
                if bClose:
                    t1td0 = tpl1i[0].to_2d(tpl1i[1][0])
                    t1td1 = tpl1i[0].to_2d(tpl1i[1][1])
                    t1td2 = tpl1i[0].to_2d(tpl1i[1][2])

                    t2td0 = tpl1i[0].to_2d(tpl2i[1][0])
                    t2td1 = tpl1i[0].to_2d(tpl2i[1][1])
                    t2td2 = tpl1i[0].to_2d(tpl2i[1][2])

                    pgon1 = Polygon_2.Polygon_2_EPECK()
                    pgon1.push_back(t1td0)
                    pgon1.push_back(t1td1)
                    pgon1.push_back(t1td2)

                    pgon2 = Polygon_2.Polygon_2_EPECK()
                    pgon2.push_back(t2td0)
                    pgon2.push_back(t2td1)
                    pgon2.push_back(t2td2)

                    pgon3 = Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()
                    CGAL.intersection(pgon1, pgon2, pgon3)

                    if len(pgon3) != 0:
                        v10 = out.add_vertex(tpl1i[1][0])
                        v11 = out.add_vertex(tpl1i[1][1])
                        v12 = out.add_vertex(tpl1i[1][2])

                        v20 = out.add_vertex(tpl2i[1][0])
                        v21 = out.add_vertex(tpl2i[1][1])
                        v22 = out.add_vertex(tpl2i[1][2])

                        out.add_face(v10, v11, v12)
                        out.add_face(v20, v21, v22)

                    """
                    for pwh in pgon3 :
                        if pwh.outer_boundary().size() == 3 :
                            obp = pwh.outer_boundary()

                            # convert back to 3d
                            v0 = tpl1i[0].to_3d(obp.vertex(0))
                            v1 = tpl1i[0].to_3d(obp.vertex(1))
                            v2 = tpl1i[0].to_3d(obp.vertex(2))

                            v0i = out.add_vertex(v0)
                            v1i = out.add_vertex(v1)
                            v2i = out.add_vertex(v2)

                            out.add_face(v0i,v1i,v2i)
                        elif pwh.outer_boundary().size() == 4 :
                            obp = pwh.outer_boundary()

                            # convert back to 3d
                            v0 = tpl1i[0].to_3d(obp.vertex(0))
                            v1 = tpl1i[0].to_3d(obp.vertex(1))
                            v2 = tpl1i[0].to_3d(obp.vertex(2))
                            v3 = tpl1i[0].to_3d(obp.vertex(3))

                            v0i = out.add_vertex(v0)
                            v1i = out.add_vertex(v1)
                            v2i = out.add_vertex(v2)
                            v3i = out.add_vertex(v3)

                            out.add_face(v0i,v1i,v2i)
                            out.add_face(v0i,v2i,v3i)
                        elif pwh.outer_boundary().size() == 6 :
                            obp = pwh.outer_boundary()

                            # convert back to 3d
                            v0 = tpl1i[0].to_3d(obp.vertex(0))
                            v1 = tpl1i[0].to_3d(obp.vertex(1))
                            v2 = tpl1i[0].to_3d(obp.vertex(2))
                            v3 = tpl1i[0].to_3d(obp.vertex(3))
                            v4 = tpl1i[0].to_3d(obp.vertex(4))
                            v5 = tpl1i[0].to_3d(obp.vertex(5))


                            v0i = out.add_vertex(v0)
                            v1i = out.add_vertex(v1)
                            v2i = out.add_vertex(v2)
                            v3i = out.add_vertex(v3)
                            v4i = out.add_vertex(v4)
                            v5i = out.add_vertex(v5)

                            out.add_face(v0i,v1i,v2i)
                            out.add_face(v0i,v2i,v3i)
                            out.add_face(v0i,v3i,v4i)
                            out.add_face(v0i,v4i,v5i)

                        else :
                            print(pwh.outer_boundary().size())
                    """

        return c

    @classmethod
    def cube(cls, center=[0, 0, 0], radius=[1, 1, 1]):
        """
        Construct an axis-aligned solid cuboid. Optional parameters are `center` and
        `radius`, which default to `[0, 0, 0]` and `[1, 1, 1]`. The radius can be
        specified using a single number or a list of three numbers, one for each axis.

        Example code::

            cube = CSG.cube(
              center=[0, 0, 0],
              radius=1
            )
        """
        c = geom.Vector(0, 0, 0)
        r = [1, 1, 1]
        if isinstance(center, list):
            c = geom.Vector(center)
        if isinstance(radius, list):
            r = radius
        else:
            r = [radius, radius, radius]

        polygons = [
            geom.Polygon(
                [
                    geom.Vertex(
                        geom.Vector(
                            c.x + r[0] * (2 * bool(i & 1) - 1),
                            c.y + r[1] * (2 * bool(i & 2) - 1),
                            c.z + r[2] * (2 * bool(i & 4) - 1),
                        )
                    )
                    for i in v[0]
                ]
            )
            for v in [
                [[0, 4, 6, 2], [-1, 0, 0]],
                [[1, 3, 7, 5], [+1, 0, 0]],
                [[0, 1, 5, 4], [0, -1, 0]],
                [[2, 6, 7, 3], [0, +1, 0]],
                [[0, 2, 3, 1], [0, 0, -1]],
                [[4, 5, 7, 6], [0, 0, +1]],
            ]
        ]
        return CSG.fromPolygons(polygons)

    def volume(self):
        return Polygon_mesh_processing.volume(self.sm)

    def area(self):
        return Polygon_mesh_processing.area(self.sm)

    def minEdgeLength(self):
        vAp = self.toVerticesAndPolygons()
        v = vAp[0]
        p = vAp[1]
        n = vAp[2]

        minEdge = 9e99
        maxEdge = -9e99

        for i, tri in enumerate(p):
            for j, vertInd in enumerate(tri):
                v1 = _np.array(v[j])
                v2 = _np.array(v[(j + 1) % 3])
                dv = v2 - v1
                mdv = _np.sqrt((dv * dv).sum())

                if mdv < minEdge:
                    minEdge = mdv
                if mdv > maxEdge:
                    maxEdge = mdv
        return minEdge

    def maxEdgeLength(self):
        vAp = self.toVerticesAndPolygons()
        v = vAp[0]
        p = vAp[1]
        n = vAp[2]

        minEdge = 9e99
        maxEdge = -9e99

        for i, tri in enumerate(p):
            for j, vertInd in enumerate(tri):
                v1 = _np.array(v[j])
                v2 = _np.array(v[(j + 1) % 3])
                dv = v2 - v1
                mdv = _np.sqrt((dv * dv).sum())

                if mdv < minEdge:
                    minEdge = mdv
                if mdv > maxEdge:
                    maxEdge = mdv
        return maxEdge

    def isNull(self):
        return self.sm.number_of_faces() == 0

    def isClosed(self):
        return CGAL.is_closed(self.sm)

    def isTriangleMesh(self):
        return CGAL.is_triangle_mesh(self.sm)

    def isOutwardOriented(self):
        return CGAL.is_outward_oriented(self.sm)

    def doesSelfIntersect(self):
        return Polygon_mesh_processing.does_self_intersect(self.sm)

    def info(self):
        return {
            "null": self.isNull(),
            "closed": self.isClosed(),
            "triangle": self.isTriangleMesh(),
            "outward": self.isOutwardOriented(),
            "volume": self.volume(),
            "area": self.area(),
            "numberfaces": self.getNumberPolys(),
            "numbervertices": self.getNumberVertices(),
            "minEdge": self.minEdgeLength(),
            "maxEdge": self.maxEdgeLength(),
        }

    def loadOff(self, fileName):
        self.sm.loadOff(fileName)

    def writeOff(self, fileName):
        self.sm.writeOff(fileName)


def do_intersect(csg1, csg2):
    return Polygon_mesh_processing.do_intersect(csg1.sm, csg2.sm)


def intersecting_meshes(csgList):
    smList = [c.sm for c in csgList]
    print(smList)


class PolygonProcessing:
    @classmethod
    def windingNumber(cls, pgon):
        """return the winding number of pgon
        :param pgon: list of points [[x1,y1], [x2,y2], ... ]
        :type pgon: List[List[x1,y1], ...]
        returns: Integer winding number
        """

        # winding angle
        wa = 0

        def mag(v):
            return (v**2).sum() ** 0.5

        def norm(v):
            return v / mag(v)

        pgon = list(pgon)
        pgon = [[p[0], p[1], 0] for p in pgon]
        pgon = _np.array(pgon)

        for pi in range(len(pgon)):
            mpi = pi % len(pgon)
            mpj = (pi + 1) % len(pgon)
            mpk = (pi + 2) % len(pgon)
            d1 = norm(pgon[mpk] - pgon[mpj])
            d0 = norm(pgon[mpj] - pgon[mpi])

            xp = _np.cross(d1, d0)
            a = _np.arcsin(mag(xp)) * _np.sign(xp[2])
            wa += a

        wa /= 2 * _np.pi

        return wa

    @classmethod
    def reversePolygon(cls, pgon):
        """return reversed polygon
        :param pgon: list of points [[x1,y1], [x2,y2], ... ]
        :type pgon: List[List[x1,y1], ...]
        returns: List[List[x1,y1], ...]
        """

        pgon = _np.array(pgon)
        return pgon[::-1]

    @classmethod
    def makePolygonFromList(cls, pgon, type=""):
        """Convert list of points [[x1,y1], [x2,y2], ... ] to cgal Polygon_2

        :param pgon: list of points [[x1,y1], [x2,y2], ... ]
        :type pgon: List[List[x,y], ..]
        :param type: Class of polygon (Polygon_2_EPICK, Polygon_2_EPECK, Partition_traits_2_Polygon_2_EPECK)
        :param type: str
        returns: Polygon_2
        """

        if type == "Partition_traits_2_Polygon_2_EPECK":
            poly2 = Partition_traits_2_Polygon_2.Partition_traits_2_Polygon_2_EPECK()
        elif type == "Polygon_2_EPECK":
            poly2 = Polygon_2.Polygon_2_EPECK()
        elif type == "Polygon_2_EPICK":
            poly2 = Polygon_2.Polygon_2_EPICK()
        else:
            poly2 = Polygon_2.Polygon_2_EPECK()

        for p in pgon:
            poly2.push_back(Point_2.Point_2_EPECK(p[0], p[1]))

        return poly2

    @classmethod
    def makeListFromPolygon(selfclas, pgon):
        """Convert 2D polygon to list of points [[x1,y1], [x2,y2], ... ]

        :param pgon: cgal Polygon_2 input
        :type pgon: Polygon_2_EPECK or Polygon_2_EPICK
        returns: [[x1,y1], [x2,y2], ...]
        """

        polyCoords = []
        for ppi in range(pgon.size()):
            pnt = pgon.vertex(ppi)
            polyCoords.append([pnt.x(), pnt.y()])

        return polyCoords

    @classmethod
    def decomposePolygon2d(cls, pgon):
        """Decompose general 2D polygon (pgon) to convex 2D polygons

        :param pgon: list of pgon points (which are lists) [[x1,y1], [x2,y2], ...]
        :type pgon: List(List[2])
        returns: List of polgons [pgon1, pgon2, ...]

        """

        poly2 = Partition_traits_2_Polygon_2.Partition_traits_2_Polygon_2_EPECK()

        for p in pgon:
            poly2.push_back(Point_2.Point_2_EPECK(p[0], p[1]))

        # pythonHelpers.draw_polygon_2(poly2)

        partPoly = Partition_traits_2_Polygon_2.List_Polygon_2_EPECK()

        Partition_traits_2_Polygon_2.optimal_convex_partition_2(poly2, partPoly)

        partPolyList = []

        for pp in partPoly:
            partPolyCoords = []
            for ppi in range(pp.size()):
                pnt = pp.vertex(ppi)
                partPolyCoords.append([pnt.x(), pnt.y()])

            # TODO check if needed
            # pnt = pp.vertex(0)
            # partPolyCoords.append([pnt.x(),pnt.y()])

            partPolyList.append(partPolyCoords)

        # pythonHelpers.draw_polygon_2_list(partPolyList)

        return partPolyList

    @classmethod
    def decomposePolygon2dWithHoles(cls, pgonOuter, pgonHoles):
        """Decompose general 2D polygon with holes (pgon) to convex 2D polygons

        :param pgonOuter: list of pgon points (which are lists) [[x1,y1], [x2,y2], ...]
        :type pgon: List(List[2])
        :param pgonHoles: List of polgons [pgon1, pgon2, ...]
        returns: List of polgons [pgon1, pgon2, ...]
        """

        poly2Boundary = cls.makePolygonFromList(pgonOuter)

        poly2WithHoles = Polygon_with_holes_2.Polygon_with_holes_2_EPECK(poly2Boundary)

        for hole in pgonHoles:
            holePoly = cls.makePolygonFromList(hole)
            poly2WithHoles.add_hole(holePoly)

        decomp = CGAL.PolygonWithHolesConvexDecomposition_2_wrapped(poly2WithHoles)

        decomPolyListList = []
        for decompPoly in decomp:
            decomPolyList = cls.makeListFromPolygon(decompPoly)
            decomPolyListList.append(decomPolyList)

        return decomPolyListList

    @classmethod
    def triangulatePolygon2d(cls, pgon):
        """Triangulate general 2D polygon

        :param pgonOuter: list of pgon points (which are lists) [[x1,y1], [x2,y2], ...]
        :type pgon: List(List[2])
        returns: List of triangles [ [[x1,y1], [x2,y2], [x3,y3]], [[x1,y1], [x2,y2], [x3,y3]], ...]
        """

        # first decompose as triangulation only works on convex hulls
        partPolyList = cls.decomposePolygon2d(pgon)
        triList = []

        # print('triangulatePolygon2d ndecom={}'.format(len(partPolyList)))

        # Loop over convex polygons and triangulate
        for partPoly in partPolyList:
            cdt = CGAL.CDT2_EPECK()

            for vert in partPoly:
                cdt.push_back(Point_2.Point_2_EPECK(vert[0], vert[1]))

            for f in cdt.all_face_handles():
                if not cdt.is_infinite(f):
                    t = cdt.triangle(f)
                    tvl = []
                    for i in [0, 1, 2]:
                        v = [t.vertex(i).x(), t.vertex(i).y()]
                        tvl.append(v)
                    triList.append(tvl)

        return triList


class PolyhedronProcessing:
    @classmethod
    def surfaceMesh_to_Polyhedron(cls, sm):
        vf = Surface_mesh.toVerticesAndPolygons(sm)

        p = Polyhedron_3.Polyhedron_3_EPECK()
        p.buildFromVertsAndFaces(vf[0], vf[1])

        return p

    @classmethod
    def nefPolyhedron_to_convexPolyhedra(cls, np):
        CGAL.convex_decomposition_3(np)
        vi = np.volume_begin()
        ve = np.volume_end()
        pList = []
        while vi != ve:
            si = vi.shells_begin()
            se = vi.shells_end()
            if vi.mark():
                while si != se:
                    p = Polyhedron_3.Polyhedron_3_EPECK()
                    np.convert_inner_shell_to_polyhedron(si, p)
                    pList.append(p)
                    si.next()
            vi.next()

        return pList

    @classmethod
    def polyhedron_to_numpyArrayPlanes(cls, p):
        return _np.array(p.convertToPlanes())

        # Following does not work, maybe because not triangles
        planes = []
        fi = p.facets_begin()
        fe = p.facets_end()
        while fi != fe:
            plane = fi.plane()
            # print(plane)
            # point = plane.point()
            print(plane.a(), plane.b(), plane.c(), plane.d())
            orthvec = plane.orthogonal_vector()

            # print(plane.point(), plane.orthogonal_vector())
            # planes.append([point.x(),point.y(),point.z(), orthvec.x(), orthvec.y(), orthvec.z()])
            fi.next()

        return _np.array(planes)
