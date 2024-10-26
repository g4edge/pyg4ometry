from .Point_3 import Point_3_ECER as _Point_3_ECER
from .Vector_3 import Vector_3_ECER as _Vector_3_ECER
from .Plane_3 import Plane_3_ECER as _Plane_3_ECER
from .Nef_polyhedron_3 import Nef_polyhedron_3_ECER as _Nef_polyhedron_3_ECER
from .Polyhedron_3 import Polyhedron_3_ECER as _Polyhedron_3_ECER
from . import Surface_mesh as _Surface_mesh
from .Surface_mesh import Surface_mesh_ECER as _Surface_mesh_ECER
from .Surface_mesh import Surface_mesh_EPECK as _Surface_mesh_EPECK
from .CGAL import copy_face_graph as _copy_face_graph


def halfPlaneMesh(planes=None):
    n1 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(0, 0, 1), _Vector_3_ECER(0, 0, 1)))
    n2 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(0, 0, -1), _Vector_3_ECER(0, 0, -1)))
    n3 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(0, 1, 0), _Vector_3_ECER(0, 1, 0)))
    n4 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(0, -1, 0), _Vector_3_ECER(0, -1, 0)))
    n5 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(1, 0, 0), _Vector_3_ECER(1, 0, 0)))
    n6 = _Nef_polyhedron_3_ECER(_Plane_3_ECER(_Point_3_ECER(-1, 0, 0), _Vector_3_ECER(-1, 0, 0)))

    n = n1 * n2 * n3 * n4 * n5 * n6

    p = _Polyhedron_3_ECER()
    n.convert_to_polyhedron(p)

    sm_ecer = _Surface_mesh_ECER()
    sm_epeck = _Surface_mesh_EPECK()

    _copy_face_graph(p, sm_ecer)
    _Surface_mesh.toCGALSurfaceMesh(sm_epeck, sm_ecer)

    return sm_epeck
