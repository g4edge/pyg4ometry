import numpy as _np
import ctypes as _ctypes
import os as _os

_lib = _ctypes.cdll.LoadLibrary(_os.path.join(_os.path.dirname(__file__),"pyg4_cgal.so"))
#_lib = _np.ctypeslib.load_library(_os.path.join(_os.path.dirname(__file__),"pyg4_cgal.so"), ".")


vertexfacet_polyhedron = _lib.pyg4_cgal_vertexfacet_polyhedron
vertexfacet_polyhedron.argtypes = [_ctypes.c_int,
                                   _ctypes.c_int,
                                   _np.ctypeslib.ndpointer(dtype=_np.uintp),
                                   _np.ctypeslib.ndpointer(dtype=_np.int, ndim=1),
                                   _np.ctypeslib.ndpointer(dtype=_np.uintp)]
vertexfacet_polyhedron.restype = _ctypes.c_void_p

delete_polyhedron = _lib.pyg4_cgal_delete_polyhedron
delete_polyhedron.argtypes = [_ctypes.c_void_p]
delete_polyhedron.restype = _ctypes.c_int