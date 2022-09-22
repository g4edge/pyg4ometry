from . import CGAL
from . import Surface_mesh
from . import Polygon_mesh_processing
from . import geom
from . import Aff_transformation_3
from . import Vector_3

import numpy as _np

class CSG :
    def __init__(self):
        self.sm = Surface_mesh.Surface_mesh_EPICK()

    @classmethod
    def fromPolygons(cls, polygons, **kwargs):
        csg = CSG()
        csg.sm = Surface_mesh.Surface_mesh_EPICK()
        Surface_mesh.toCGALSurfaceMesh(csg.sm, polygons)
        Polygon_mesh_processing.triangulate_faces(csg.sm)
        return csg

    def clone(self):
        csg = CSG()
        csg.sm = self.sm.clone()
        return csg

    def rotate(self,axisIn,angleDeg):
        rot = _np.zeros((3,3))

        axis = geom.Vector(axisIn)

        normAxis = axis / axis.length()

        cosAngle = _np.cos(angleDeg / 180.0 * _np.pi)
        sinAngle = _np.sin(angleDeg / 180.0 * _np.pi)
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

        rotn = Aff_transformation_3.Aff_transformation_3_EPICK(rot[0][0], rot[0][1], rot[0][2],
                                                               rot[1][0], rot[1][1], rot[1][2],
                                                               rot[2][0], rot[2][1], rot[2][2],1);
        Polygon_mesh_processing.transform(rotn, self.sm)

    def translate(self,disp):
        vIn = geom.Vector(disp)
        # TODO tidy vector usage (i.e conversion in geom?)
        v = Vector_3.Vector_3_EPICK(vIn[0],vIn[1],vIn[2])
        transl = Aff_transformation_3.Aff_transformation_3_EPICK(CGAL.Translation(), v)
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
        scal = Aff_transformation_3.Aff_transformation_3_EPICK(x, 0, 0,
                                                               0, y, 0,
                                                               0, 0, z,1)
        Polygon_mesh_processing.transform(scal, self.sm)

    def toVerticesAndPolygons(self):
        return Surface_mesh.toVerticesAndPolygons(self.sm)

    def getNumberPolys(self) :
        return self.sm.number_of_faces()

    def vertexCount(self) :
        return self.sm.number_of_vertices()

    def polygonCount(self) :
        return self.sm.number_of_faces()

    def intersect(self, csg2):
        out = Surface_mesh.Surface_mesh_EPICK()
        Polygon_mesh_processing.corefine_and_compute_intersection(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    def union(self, csg2):
        out = Surface_mesh.Surface_mesh_EPICK()
        Polygon_mesh_processing.corefine_and_compute_union(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    def subtract(self, csg2):
        out = Surface_mesh.Surface_mesh_EPICK()
        Polygon_mesh_processing.corefine_and_compute_difference(self.sm,csg2.sm,out)
        csg = CSG()
        csg.sm = out
        return csg

    # TODO finish coplanar intersection
    def coplanarIntersection(self, csg) :
        return CSG()

    def isNull(self):
        return self.sm.number_of_faces() == 0

    def volume(self):
        return Polygon_mesh_processing.volume(self.sm)

    def area(self) :
        return Polygon_mesh_processing.area(self.sm)

def do_intersect(m1, m2) :
    return Polygon_mesh_processing.do_intersect(m1,m2)