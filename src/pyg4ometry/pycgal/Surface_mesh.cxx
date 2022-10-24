#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                 Point_3_EPICK;
typedef Kernel_EPICK::Vector_3                                Vector_3_EPICK;
typedef CGAL::Surface_mesh<Kernel_EPICK::Point_3>             Surface_mesh_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                 Point_3_EPECK;
typedef Kernel_EPECK::Vector_3                                Vector_3_EPECK;
typedef CGAL::Surface_mesh<Kernel_EPECK::Point_3>             Surface_mesh_EPECK;

#include "geom.h"

namespace std
{
  inline void hash_combine(std::size_t) {}

  template <typename T, typename... Rest>
  inline void hash_combine(std::size_t &seed, const T &v, Rest... rest) {
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    std::hash_combine(seed, rest...);
  }

  template<> struct hash<Surface_mesh_EPICK> {
    std::size_t operator()(const Surface_mesh_EPICK &sm) const {
      using std::size_t;
      using std::hash;

      std::size_t h = 0;

      // loop over vertices
      Surface_mesh_EPICK::Point p;
      for(Surface_mesh_EPICK::Vertex_index vd : sm.vertices()) {
        p = sm.point(vd);
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.x())));
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.y())));
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.z())));
      }

      // loop over faces
      /*
      for(Surface_mesh::Face_index fd : sm->faces()) {
        for(Surface_mesh::Halfedge_index hd :  CGAL::halfedges_around_face(sm->halfedge(fd),*sm)) {
          // std::hash_combine(h,std::hash<int>()((int)sm->source(hd)));
        }
      }
      */

      return h;
    }
  };
}

py::list* toVerticesAndPolygons(Surface_mesh_EPICK &sm) {
  py::list *verts = new py::list();
  py::list *polys = new py::list();

  Point_3_EPICK p;
  for(Surface_mesh_EPICK::Vertex_index vd : sm.vertices()) {
    py::list *v = new py::list();
    p = sm.point(vd);
    v->append(CGAL::to_double(p.x()));
    v->append(CGAL::to_double(p.y()));
    v->append(CGAL::to_double(p.z()));
    verts->append(v);
  }

  int iCount = 0;
  for(Surface_mesh_EPICK::Face_index fd : sm.faces()) {
    py::list *p = new py::list();
    for(Surface_mesh_EPICK::Halfedge_index hd :  CGAL::halfedges_around_face(sm.halfedge(fd),sm)) {
      p->append((int)sm.source(hd));
    }
    polys->append(p);
    ++iCount;
  }

  py::list *ret = new py::list();
  ret->append(verts);
  ret->append(polys);
  ret->append(iCount);

  return ret;
}

void toCGALSurfaceMesh(Surface_mesh_EPICK &sm, py::list &polygons) {

  std::vector<Vector> verts;
  std::vector<std::vector<unsigned int>> polys;

  /////////////////////////////////////////////////////////////
  std::hash<std::string> hash;
  std::map<size_t, unsigned int> vertexIndexMap;

  unsigned int count = 0;

  double offset = 1.234567890; // gives unique key

  for(auto polyHandle : polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();

    std::vector<unsigned int> cell;
    for (auto vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>();

      // coordinates of vertex
      double x = vert->pos().x();
      double y = vert->pos().y();
      double z = vert->pos().z();

      // sign of 0
      if(fabs(x) < 1e-11) x = 0;
      if(fabs(y) < 1e-11) y = 0;
      if(fabs(z) < 1e-11) z = 0;

      // create "unique" hash
      std::ostringstream sstream;
      sstream.precision(11);
      sstream << std::fixed;
      sstream << x+offset << " " << y+offset << " " << z+offset;
      size_t posHash = hash(sstream.str());

      // check if not in in map
      if (vertexIndexMap.find(posHash) == vertexIndexMap.end()) {
	    vertexIndexMap.insert(std::pair<size_t, unsigned int>(posHash,verts.size()));
	    verts.push_back(vert->pos());
      }

      cell.push_back(vertexIndexMap.find(posHash)->second);
      count++;
    }
    polys.push_back(cell);
  }

  for(auto v : verts) {
    sm.add_vertex(Point_3_EPICK(v._x,v._y, v._z));
  }

  for(auto f : polys) {

    if(f.size() == 3) {
      sm.add_face(Surface_mesh_EPICK::Vertex_index((size_t)f[0]),
                  Surface_mesh_EPICK::Vertex_index((size_t)f[1]),
                  Surface_mesh_EPICK::Vertex_index((size_t)f[2]));
    }
    else if(f.size() == 4) {
      sm.add_face(Surface_mesh_EPICK::Vertex_index((size_t)f[0]),
                  Surface_mesh_EPICK::Vertex_index((size_t)f[1]),
                  Surface_mesh_EPICK::Vertex_index((size_t)f[2]),
                  Surface_mesh_EPICK::Vertex_index((size_t)f[3]));
    }
    // TODO
    //else {
    //  sm.add_face(f);
    //}
  }
}

py::list* toVerticesAndPolygons(Surface_mesh_EPECK &sm) {
  py::list *verts = new py::list();
  py::list *polys = new py::list();

  Point_3_EPECK p;
  for(Surface_mesh_EPECK::Vertex_index vd : sm.vertices()) {
    py::list *v = new py::list();
    p = sm.point(vd);
    v->append(CGAL::to_double(p.x()));
    v->append(CGAL::to_double(p.y()));
    v->append(CGAL::to_double(p.z()));
    verts->append(v);
  }

  int iCount = 0;
  for(Surface_mesh_EPECK::Face_index fd : sm.faces()) {
    py::list *p = new py::list();
    for(Surface_mesh_EPECK::Halfedge_index hd :  CGAL::halfedges_around_face(sm.halfedge(fd),sm)) {
      p->append((int)sm.source(hd));
    }
    polys->append(p);
    ++iCount;
  }

  py::list *ret = new py::list();
  ret->append(verts);
  ret->append(polys);
  ret->append(iCount);

  return ret;
}

void toCGALSurfaceMesh(Surface_mesh_EPECK &sm, py::list &polygons) {

  std::vector<Vector> verts;
  std::vector<std::vector<unsigned int>> polys;

  /////////////////////////////////////////////////////////////
  std::hash<std::string> hash;
  std::map<size_t, unsigned int> vertexIndexMap;

  unsigned int count = 0;

  double offset = 1.234567890; // gives unique key

  for(auto polyHandle : polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();

    std::vector<unsigned int> cell;
    for (auto vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>();

      // coordinates of vertex
      double x = vert->pos().x();
      double y = vert->pos().y();
      double z = vert->pos().z();

      // sign of 0
      if(fabs(x) < 1e-11) x = 0;
      if(fabs(y) < 1e-11) y = 0;
      if(fabs(z) < 1e-11) z = 0;

      // create "unique" hash
      std::ostringstream sstream;
      sstream.precision(11);
      sstream << std::fixed;
      sstream << x+offset << " " << y+offset << " " << z+offset;
      size_t posHash = hash(sstream.str());

      // check if not in in map
      if (vertexIndexMap.find(posHash) == vertexIndexMap.end()) {
	    vertexIndexMap.insert(std::pair<size_t, unsigned int>(posHash,verts.size()));
	    verts.push_back(vert->pos());
      }

      cell.push_back(vertexIndexMap.find(posHash)->second);
      count++;
    }
    polys.push_back(cell);
  }

  for(auto v : verts) {
    sm.add_vertex(Point_3_EPECK(v._x,v._y, v._z));
  }

  for(auto f : polys) {

    if(f.size() == 3) {
      sm.add_face(Surface_mesh_EPECK::Vertex_index((size_t)f[0]),
                  Surface_mesh_EPECK::Vertex_index((size_t)f[1]),
                  Surface_mesh_EPECK::Vertex_index((size_t)f[2]));
    }
    else if(f.size() == 4) {
      sm.add_face(Surface_mesh_EPECK::Vertex_index((size_t)f[0]),
                  Surface_mesh_EPECK::Vertex_index((size_t)f[1]),
                  Surface_mesh_EPECK::Vertex_index((size_t)f[2]),
                  Surface_mesh_EPECK::Vertex_index((size_t)f[3]));
    }
    // TODO
    //else {
    //  sm.add_face(f);
    //}
  }
}

PYBIND11_MODULE(Surface_mesh, m) {
  py::class_<Surface_mesh_EPICK::Vertex_index>(m,"Vertex_index_EPICK")
    .def(py::init<>());
  py::class_<Surface_mesh_EPICK::Face_index>(m,"Face_index_EPICK");
  py::class_<Surface_mesh_EPICK::Halfedge_index>(m,"Halfedge_index_EPICK");
  py::class_<Surface_mesh_EPICK::Edge_index>(m,"Edge_index_EPICK");

  py::class_<Surface_mesh_EPICK>(m,"Surface_mesh_EPICK")
    .def(py::init<>())

    /* Not part of the CGAL API */
    .def("clone",[](Surface_mesh_EPICK &sm) {return Surface_mesh_EPICK(sm);})
    .def("hash",[](Surface_mesh_EPICK &sm) {return std::hash<Surface_mesh_EPICK>{}(sm);})

    /* Adding Vertices, Edges, and Faces */
    .def("add_vertex",[](Surface_mesh_EPICK &sm) {return sm.add_vertex();})
    .def("add_vertex",[](Surface_mesh_EPICK &sm, Point_3_EPICK &p) {return sm.add_vertex(p);})
    .def("add_edge",[](Surface_mesh_EPICK &sm) {return sm.add_edge();})
    .def("add_edge",[](Surface_mesh_EPICK &sm, Surface_mesh_EPICK::Vertex_index &v0, Surface_mesh_EPICK::Vertex_index &v1) {return sm.add_edge(v0,v1);})
    .def("add_face",[](Surface_mesh_EPICK &sm) {sm.add_face();})
    // TODO
    //.def("add_face",[](Surface_mesh &sm, Range vertices) {sm.add_face(vertices);})
    .def("add_face",[](Surface_mesh_EPICK &sm, Surface_mesh_EPICK::Vertex_index &v0, Surface_mesh_EPICK::Vertex_index &v1, Surface_mesh_EPICK::Vertex_index &v2) {return sm.add_face(v0,v1,v2);})
    .def("add_face",[](Surface_mesh_EPICK &sm, Surface_mesh_EPICK::Vertex_index &v0, Surface_mesh_EPICK::Vertex_index &v1, Surface_mesh_EPICK::Vertex_index &v2, Surface_mesh_EPICK::Vertex_index &v3) {return sm.add_face(v0,v1,v2,v3);})

    /* Memory management */
    .def("number_of_vertices",[](Surface_mesh_EPICK &sm){return sm.number_of_vertices();})
    .def("number_of_halfedges",[](Surface_mesh_EPICK &sm){return sm.number_of_halfedges();})
    .def("number_of_edges",[](Surface_mesh_EPICK &sm){return sm.number_of_edges();})
    .def("number_of_faces",[](Surface_mesh_EPICK &sm){return sm.number_of_faces();})
    .def("is_empty",[](Surface_mesh_EPICK &sm){return sm.is_empty();})
    // TODO CGAL version
    .def("clear_without_removing_property_maps",[](Surface_mesh_EPICK &sm) {sm.clear_without_removing_property_maps();})
    .def("clear",[](Surface_mesh_EPICK &sm) {sm.clear();});

    /* Validity checks */

  m.def("toCGALSurfaceMesh",[](Surface_mesh_EPICK &sm, py::list &polygons) {toCGALSurfaceMesh(sm,polygons);});
  m.def("toVerticesAndPolygons",[](Surface_mesh_EPICK &sm) {return toVerticesAndPolygons(sm);});

  py::class_<Surface_mesh_EPECK>(m,"Surface_mesh_EPECK")
    .def(py::init<>())

    /* Not part of the CGAL API */
    .def("clone",[](Surface_mesh_EPECK &sm) {return Surface_mesh_EPECK(sm);})
    //.def("hash",[](Surface_mesh_EPECK &sm) {return std::hash<Surface_mesh_EPECK>{}(sm);})

    /* Adding Vertices, Edges, and Faces */
    .def("add_vertex",[](Surface_mesh_EPECK &sm) {return sm.add_vertex();})
    .def("add_vertex",[](Surface_mesh_EPECK &sm, Point_3_EPECK &p) {return sm.add_vertex(p);})
    .def("add_edge",[](Surface_mesh_EPECK &sm) {return sm.add_edge();})
    .def("add_edge",[](Surface_mesh_EPECK &sm, Surface_mesh_EPECK::Vertex_index &v0, Surface_mesh_EPECK::Vertex_index &v1) {return sm.add_edge(v0,v1);})
    .def("add_face",[](Surface_mesh_EPECK &sm) {sm.add_face();})
    // TODO
    //.def("add_face",[](Surface_mesh &sm, Range vertices) {sm.add_face(vertices);})
    .def("add_face",[](Surface_mesh_EPECK &sm, Surface_mesh_EPECK::Vertex_index &v0, Surface_mesh_EPECK::Vertex_index &v1, Surface_mesh_EPECK::Vertex_index &v2) {return sm.add_face(v0,v1,v2);})
    .def("add_face",[](Surface_mesh_EPECK &sm, Surface_mesh_EPECK::Vertex_index &v0, Surface_mesh_EPECK::Vertex_index &v1, Surface_mesh_EPECK::Vertex_index &v2, Surface_mesh_EPECK::Vertex_index &v3) {return sm.add_face(v0,v1,v2,v3);})

    /* Memory management */
    .def("number_of_vertices",[](Surface_mesh_EPECK &sm){return sm.number_of_vertices();})
    .def("number_of_halfedges",[](Surface_mesh_EPECK &sm){return sm.number_of_halfedges();})
    .def("number_of_edges",[](Surface_mesh_EPECK &sm){return sm.number_of_edges();})
    .def("number_of_faces",[](Surface_mesh_EPECK &sm){return sm.number_of_faces();})
    .def("is_empty",[](Surface_mesh_EPECK &sm){return sm.is_empty();})
    // TODO CGAL version
    .def("clear_without_removing_property_maps",[](Surface_mesh_EPECK &sm) {sm.clear_without_removing_property_maps();})
    .def("clear",[](Surface_mesh_EPECK &sm) {sm.clear();});

    /* Validity checks */

  m.def("toCGALSurfaceMesh",[](Surface_mesh_EPECK &sm, py::list &polygons) {toCGALSurfaceMesh(sm,polygons);});
  m.def("toVerticesAndPolygons",[](Surface_mesh_EPECK &sm) {return toVerticesAndPolygons(sm);});
}
