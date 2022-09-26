from . import CGAL
from . import Surface_mesh
from . import Polygon_mesh_processing
from . import geom
from . import Aff_transformation_3
from . import Vector_3
from . import Point_2
from . import Polygon_2
from . import Polyhedron_3

import numpy as _np

class CSG :
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

    def rotate(self,axisIn,angleDeg):
        rot = _np.zeros((3,3))

        axis = geom.Vector(axisIn)

        normAxis = axis / axis.length()

        cosAngle = _np.cos(-angleDeg / 180.0 * _np.pi)
        sinAngle = _np.sin(-angleDeg / 180.0 * _np.pi)
        verSin   = 1 - cosAngle

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

        rotn = Aff_transformation_3.Aff_transformation_3_EPECK(rot[0][0], rot[0][1], rot[0][2],
                                                               rot[1][0], rot[1][1], rot[1][2],
                                                               rot[2][0], rot[2][1], rot[2][2],1);
        Polygon_mesh_processing.transform(rotn, self.sm)

    def translate(self,disp):
        vIn = geom.Vector(disp)
        # TODO tidy vector usage (i.e conversion in geom?)
        v = Vector_3.Vector_3_EPECK(vIn[0],vIn[1],vIn[2])
        transl = Aff_transformation_3.Aff_transformation_3_EPECK(CGAL.Translation(), v)
        Polygon_mesh_processing.transform(transl, self.sm)

    # TODO need to finish and check signatures
    def scale(self, *args):
        if len(args) == 3: # x,y,z
            x = args[0]
            y = args[1]
            z = args[2]
        elif len(args) == 1 :
            if type(args[0]) is list :
                x = args[0][0]
                y = args[0][1]
                z = args[0][2]
            else : # Vector
                x = args[0][0]
                y = args[0][1]
                z = args[0][2]
        else :
            x = 1
            y = 1
            z = 1
        scal = Aff_transformation_3.Aff_transformation_3_EPECK(x, 0, 0,
                                                               0, y, 0,
                                                               0, 0, z,1)
        Polygon_mesh_processing.transform(scal, self.sm)

    def getNumberPolys(self) :
        return self.sm.number_of_faces()

    def vertexCount(self) :
        return self.sm.number_of_vertices()

    def polygonCount(self) :
        return self.sm.number_of_faces()

    def intersect(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_intersection(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    def union(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_union(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    def subtract(self, csg2):
        out = Surface_mesh.Surface_mesh_EPECK()
        Polygon_mesh_processing.corefine_and_compute_difference(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    # TODO finish coplanar intersection
    def coplanarIntersection(self, csg) :
        # print('core coplanarIntersection : has bugs for cgal meshing, switch to pycsg in config')
        return CSG()

        from ..pycsg import core as _core
        from ..pycsg import geom as _geom

        def convertFromLists(vpl):
            polyList = []
            for p in vpl[1]:
                v1 = _geom.Vertex(vpl[0][p[0]])
                v2 = _geom.Vertex(vpl[0][p[1]])
                v3 = _geom.Vertex(vpl[0][p[2]])
                poly = _geom.Polygon([v1, v2, v3])
                polyList.append(poly)
            return polyList


        vpl1 = self.toVerticesAndPolygons()
        vpl2 = csg.toVerticesAndPolygons()

        csg1 = _core.CSG.fromPolygons(convertFromLists(vpl1))
        csg2 = _core.CSG.fromPolygons(convertFromLists(vpl2))

        #print(vpl1)
        #print(csg1.polygons)

        # print(csg1.polygons)
        print('before coplanar call',type(csg1),type(csg2))
        inter = csg1.coplanarIntersection(csg2)
        print('after coplanar call',type(inter),inter.polygons)

        c = CSG()
        out = Surface_mesh.Surface_mesh_EPECK()

        #for p in inter.polygons :
        #    print(p)
        #    for v in p.vertices :
        #        print(v)

        # Surface_mesh.toCGALSurfaceMesh(out,list(inter.toVerticesAndPolygons()))
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
        if isinstance(center, list): c = geom.Vector(center)
        if isinstance(radius, list):
            r = radius
        else:
            r = [radius, radius, radius]

        polygons = list([geom.Polygon(
            list([geom.Vertex(
                geom.Vector(
                    c.x + r[0] * (2 * bool(i & 1) - 1),
                    c.y + r[1] * (2 * bool(i & 2) - 1),
                    c.z + r[2] * (2 * bool(i & 4) - 1)
                )) for i in v[0]])) for v in [
            [[0, 4, 6, 2], [-1, 0, 0]],
            [[1, 3, 7, 5], [+1, 0, 0]],
            [[0, 1, 5, 4], [0, -1, 0]],
            [[2, 6, 7, 3], [0, +1, 0]],
            [[0, 2, 3, 1], [0, 0, -1]],
            [[4, 5, 7, 6], [0, 0, +1]]
        ]])
        return CSG.fromPolygons(polygons)

    def isNull(self):
        return self.sm.number_of_faces() == 0

    def volume(self):
        return Polygon_mesh_processing.volume(self.sm)

    def area(self) :
        return Polygon_mesh_processing.area(self.sm)

def do_intersect(csg1, csg2) :
    return Polygon_mesh_processing.do_intersect(csg1.sm,csg2.sm)

def intersecting_meshes(csgList) :

    smList = [c.sm for c in csgList]
    print(smList)

class PolygonProcessing :

    @classmethod
    def decomposePolygon2d(cls, pgon) :
        poly2 = Polygon_2.Polygon_2_EPECK()
        for p in pgon :
            poly2.push_back(Point_2.Point_2_EPECK(p[0],p[1]))

        partPoly = Polygon_2.List_Polygon_2_EPECK()
        # TODO change function name (test)
        Polygon_2.test(poly2, partPoly)

        partPolyList = []

        for pp in partPoly :

            partPolyCoords = []
            for ppi in range(0,pp.size()) :
                pnt = pp.vertex(ppi)
                partPolyCoords.append([pnt.x(),pnt.y()])

            partPolyList.append(partPolyCoords)
        return partPolyList

class PolyhedronProcessing :

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
        while vi != ve :
            si = vi.shells_begin()
            se = vi.shells_end()
            if vi.mark() :
                while si != se :
                    p = Polyhedron_3.Polyhedron_3_EPECK()
                    np.convert_inner_shell_to_polyhedron(si,p)
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
        while fi != fe :

            plane = fi.plane()
            print(plane)
            # point = plane.point()
            print(plane.a(),plane.b(),plane.c(),plane.d())
            orthvec = plane.orthogonal_vector()

            #print(plane.point(), plane.orthogonal_vector())
            #planes.append([point.x(),point.y(),point.z(), orthvec.x(), orthvec.y(), orthvec.z()])
            fi.next()

        return _np.array(planes)