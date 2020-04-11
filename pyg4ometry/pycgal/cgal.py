import numpy as _np
import ctypes as _ctypes
import os as _os
import numpy as _np

_lib = _ctypes.cdll.LoadLibrary(_os.path.join(_os.path.dirname(__file__),
                                              "pyg4_cgal.so")
                                )

vertexfacet_to_polyhedron = _lib.pyg4_cgal_vertexfacet_to_polyhedron
vertexfacet_to_polyhedron.argtypes = [_ctypes.c_int,_ctypes.c_int,
                                      _np.ctypeslib.ndpointer(dtype=_np.uintp),
                                      _np.ctypeslib.ndpointer(dtype=_np.int, ndim=1),
                                      _np.ctypeslib.ndpointer(dtype=_np.uintp)]
vertexfacet_to_polyhedron.restype = _ctypes.c_void_p

convexpolyhedron_to_planes = _lib.pyg4_cgal_convexpolyhedron_to_planes
convexpolyhedron_to_planes.argtypes = [_ctypes.c_void_p,
                                       _ctypes.POINTER(_ctypes.c_int),
                                       _np.ctypeslib.ndpointer(dtype=_np.uintp)]
convexpolyhedron_to_planes.restype = _ctypes.c_int


surfacemesh_print          = _lib.pyg4_cgal_surfacemesh_print
surfacemesh_print.argtypes = [_ctypes.c_void_p]

polyhedron_write          = _lib.pyg4_cgal_polyhedron_write
polyhedron_write.argtypes = [_ctypes.c_void_p,
                             _ctypes.c_char_p]

nefpolyhedron_write          = _lib.pyg4_cgal_nefpolyhedron_write
nefpolyhedron_write.argtypes = [_ctypes.c_void_p,
                                _ctypes.c_char_p]

surfacemesh_write          = _lib.pyg4_cgal_surfacemesh_write
surfacemesh_write.argtypes = [_ctypes.c_void_p,
                             _ctypes.c_char_p]

polyhedron_print          = _lib.pyg4_cgal_polyhedron_print
polyhedron_print.argtypes = [_ctypes.c_void_p]

nefpolyhedron_print          = _lib.pyg4_cgal_nefpolyhedron_print
nefpolyhedron_print.argtypes = [_ctypes.c_void_p]

delete_polyhedron          = _lib.pyg4_cgal_delete_polyhedron
delete_polyhedron.argtypes = [_ctypes.c_void_p]
delete_polyhedron.restype  = _ctypes.c_int

delete_nefpolyhedron          = _lib.pyg4_cgal_delete_nefpolyhedron
delete_nefpolyhedron.argtypes = [_ctypes.c_void_p]
delete_nefpolyhedron.restype  = _ctypes.c_int

delete_surfacemesh          = _lib.pyg4_cgal_delete_surfacemesh
delete_surfacemesh.argtypes = [_ctypes.c_void_p]
delete_surfacemesh.restype  = _ctypes.c_int

polyhedron_to_nefpolyhedron          = _lib.pyg4_cgal_polyhedron_to_nefpolyhedron
polyhedron_to_nefpolyhedron.argtypes = [_ctypes.c_void_p]
polyhedron_to_nefpolyhedron.restype  = _ctypes.c_void_p

nefpolyhedron_to_polyhedron          = _lib.pyg4_cgal_nefpolyhedron_to_polyhedron
nefpolyhedron_to_polyhedron.argtypes = [_ctypes.c_void_p]
nefpolyhedron_to_polyhedron.restype  = _ctypes.c_void_p

nefpolyhedron_to_surfacemesh          = _lib.pyg4_cgal_nefpolyhedron_to_surfacemesh
nefpolyhedron_to_surfacemesh.argtypes = [_ctypes.c_void_p]
nefpolyhedron_to_surfacemesh.restype  = _ctypes.c_void_p

nefpolyhedron_to_convexpolyhedra          = _lib.pyg4_cgal_nefpolyhedron_to_convexpolyhedra
nefpolyhedron_to_convexpolyhedra.argtypes = [_ctypes.c_void_p,_ctypes.c_void_p*1000, _ctypes.POINTER(_ctypes.c_int)]
nefpolyhedron_to_convexpolyhedra.restypes = _np.ctypeslib.ndpointer(dtype=_np.uintp, ndim=1)


def pycsgmesh2NefPolyhedron(mesh) :
    verts, polys, count = mesh.toVerticesAndPolygons()

    verts = _np.array(verts)
    npolyvert = []
    for p in polys:
        npolyvert.append(len(p))
    npolyvert = _np.array(npolyvert)
    polys = _np.array(polys)

    vertspp = (verts.__array_interface__['data'][0] +
               _np.arange(verts.shape[0]) * verts.strides[0]).astype(_np.uintp)
    polyspp = (polys.__array_interface__['data'][0] +
               _np.arange(polys.shape[0]) * polys.strides[0]).astype(_np.uintp)

    polyhedron = vertexfacet_to_polyhedron(len(verts),
                                           len(polys),
                                           vertspp,
                                           npolyvert,
                                           polyspp)
    nefpolyhedron = polyhedron_to_nefpolyhedron(polyhedron)
    delete_polyhedron(polyhedron)

    return nefpolyhedron

