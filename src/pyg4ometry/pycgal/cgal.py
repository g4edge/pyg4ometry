import ctypes as _ctypes
import os as _os
import numpy as _np
import copy as _copy

# find pyg4_cgal....so library

g = _os.walk(_os.path.dirname(__file__))

for p in g :
    if p[0].find("pycgal") != -1 :
        f = p[2]
        for fn in f :
            if fn.find("pyg4_cgal.cpython") != -1 :
                _lib = _ctypes.cdll.LoadLibrary(_os.path.join(_os.path.dirname(__file__),
                                                              fn))

vertexfacet_to_polyhedron = _lib.pyg4_cgal_vertexfacet_to_polyhedron
vertexfacet_to_polyhedron.argtypes = [_ctypes.c_int,
                                      _ctypes.c_int,
                                      _np.ctypeslib.ndpointer(dtype=_np.uintp),
                                      _np.ctypeslib.ndpointer(dtype=_np.int, ndim=1),
                                      _np.ctypeslib.ndpointer(dtype=_np.uintp),
                                      _ctypes.c_bool]
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
nefpolyhedron_to_convexpolyhedra.argtypes = [_ctypes.c_void_p,_ctypes.c_void_p*10000, _ctypes.POINTER(_ctypes.c_int)]
nefpolyhedron_to_convexpolyhedra.restype  = _ctypes.c_int

vertex_to_polygon          = _lib.pyg4_cgal_vertex_to_polygon
vertex_to_polygon.argtypes = [_np.ctypeslib.ndpointer(dtype=_np.uintp), _ctypes.c_int, _ctypes.c_bool]
vertex_to_polygon.restype = _ctypes.c_void_p

polygon_to_vertex          = _lib.pyg4_cgal_polygon_to_vertex
polygon_to_vertex.argtypes = [_ctypes.c_void_p,_np.ctypeslib.ndpointer(dtype=_np.uintp), _ctypes.POINTER(_ctypes.c_int)]
polygon_to_vertex.restype = _ctypes.c_int

delete_polygon             = _lib.pyg4_cgal_delete_polygon
delete_polygon.argtypes    = [_ctypes.c_void_p]
delete_polygon.restype     = _ctypes.c_int

polygon_to_convexpolygons   = _lib.pyg4_cgal_polygon_to_convexpolygons
polygon_to_convexpolygons.argtypes   = [_ctypes.c_void_p,_ctypes.c_void_p*10000, _ctypes.POINTER(_ctypes.c_int)]
polygon_to_convexpolygons.restype    = _ctypes.c_int

delete_polygonlist         = _lib.pyg4_cgal_delete_polygonlist
delete_polygonlist.argtypes= [_ctypes.c_void_p]
delete_polygonlist.restype = _ctypes.c_int


def pycsgmesh2NefPolyhedron(mesh) :
    verts, polys, count = mesh.toVerticesAndPolygons()

    verts = _np.array(verts)
    polyarray = _np.zeros((len(polys),30),dtype=int)
    npolyvert = []
    for p,i  in zip(polys,range(0,len(polys))):
        npolyvert.append(len(p))
        for j in range(0,len(p)) :
            polyarray[i][j] = p[j]

    npolyvert = _np.array(npolyvert)
    polys = _np.array(polys)
    polys = polyarray

    vertspp = (verts.__array_interface__['data'][0] +
               _np.arange(verts.shape[0]) * verts.strides[0]).astype(_np.uintp)
    polyspp = (polys.__array_interface__['data'][0] +
               _np.arange(polys.shape[0]) * polys.strides[0]).astype(_np.uintp)
    polyarraypp = (polyarray.__array_interface__['data'][0] +
                   _np.arange(polyarray.shape[0]) * polyarray.strides[0]).astype(_np.uintp)

    polyhedron = vertexfacet_to_polyhedron(len(verts),
                                           len(polys),
                                           vertspp,
                                           npolyvert,
                                           polyarraypp,
                                           _ctypes.c_bool(False))

    nefpolyhedron = polyhedron_to_nefpolyhedron(polyhedron)
    delete_polyhedron(polyhedron)

    return nefpolyhedron

def pycsgmeshWritePolygon(mesh, fileName = "mesh.pol") :
    verts, polys, count = mesh.toVerticesAndPolygons()

    verts = _np.array(verts)
    polyarray = _np.zeros((len(polys),4),dtype=int)
    npolyvert = []
    for p,i  in zip(polys,range(0,len(polys))):
        npolyvert.append(len(p))
        for j in range(0,len(p)) :
            polyarray[i][j] = p[j]

    npolyvert = _np.array(npolyvert)
    polys = _np.array(polys)
    polys = polyarray

    f = open(fileName,"w")
    f.write("OFF\n")
    f.write(str(len(verts))+" "+str(len(polys))+" 0\n")
    f.write("\n")
    for v in verts :
        f.write(str(v[0])+" "+str(v[1])+" "+str(v[2])+"\n")

    for n, p in zip(npolyvert, polys) :
        f.write(str(n)+" ")
        for pv in p :
            f.write(str(pv)+" ")
        f.write("\n")

    f.close()


def numpyPolygonConvex(polygonnp):
    polygonpp = (polygonnp.__array_interface__['data'][0] +
                 _np.arange(polygonnp.shape[0]) * polygonnp.strides[0]).astype(_np.uintp)

    nconvex = _ctypes.c_int(0)
    vpArray = _ctypes.c_void_p*10000;
    polygons = vpArray()


    polygon = vertex_to_polygon(polygonpp,len(polygonnp),_ctypes.c_bool(False))
    polygon_to_convexpolygons(polygon,polygons,_ctypes.byref(nconvex))

    nverts = _ctypes.c_int(0)

    polyvertsnp = _np.zeros((1000,2))
    polyvertspp = (polyvertsnp.__array_interface__['data'][0] +
                _np.arange(polyvertsnp.shape[0]) * polyvertsnp.strides[0]).astype(_np.uintp)

    polygonList = []

    for i in range(0,nconvex.value):
        polygon_to_vertex(polygons[i],polyvertspp,_ctypes.byref(nverts))

        # no idea why this copy is needed
        polygonList.append(_copy.deepcopy(polyvertsnp[0:nverts.value][:]))

        delete_polygon(polygons[i])

    delete_polygon(polygon)

    return polygonList
