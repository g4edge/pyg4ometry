#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel;
typedef Kernel::Point_3                                       Point;
typedef Kernel::Vector_3                                      Vector_3;
typedef CGAL::Surface_mesh<Kernel::Point_3>                   Surface_mesh;

#include "geom.h"


void toCGALSurfaceMesh(Surface_mesh &sm, py::list &polygons) {

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
    sm.add_vertex(Point(v._x,v._y, v._z));
  }

  for(auto f : polys) {

    if(f.size() == 3) {
      sm.add_face(Surface_mesh::Vertex_index((size_t)f[0]),
                  Surface_mesh::Vertex_index((size_t)f[1]),
                  Surface_mesh::Vertex_index((size_t)f[2]));
    }
    else if(f.size() == 4) {
      sm.add_face(Surface_mesh::Vertex_index((size_t)f[0]),
                  Surface_mesh::Vertex_index((size_t)f[1]),
                  Surface_mesh::Vertex_index((size_t)f[2]),
                  Surface_mesh::Vertex_index((size_t)f[3]));
    }
    // TODO
    //else {
    //  sm.add_face(f);
    //}
  }
}

PYBIND11_MODULE(Surface_mesh, m) {
  py::class_<Surface_mesh::Vertex_index>(m,"Vertex_index")
    .def(py::init<>());
  py::class_<Surface_mesh::Face_index>(m,"Face_index");
  py::class_<Surface_mesh::Halfedge_index>(m,"Halfedge_index");
  py::class_<Surface_mesh::Edge_index>(m,"Edge_index");

  py::class_<Point>(m,"Point")
    .def(py::init<int, int, int>())
    .def(py::init<double, double, double>());

  py::class_<Surface_mesh>(m,"Surface_mesh")
    .def(py::init<>())
    /* Adding Vertices, Edges, and Faces */
    .def("add_vertex",[](Surface_mesh &sm) {return sm.add_vertex();})
    .def("add_vertex",[](Surface_mesh &sm, Point &p) {return sm.add_vertex(p);})
    .def("add_edge",[](Surface_mesh &sm) {return sm.add_edge();})
    .def("add_edge",[](Surface_mesh &sm, Surface_mesh::Vertex_index &v0, Surface_mesh::Vertex_index &v1) {return sm.add_edge(v0,v1);})
    .def("add_face",[](Surface_mesh &sm) {sm.add_face();})
    // TODO
    //.def("add_face",[](Surface_mesh &sm, Range vertices) {sm.add_face(vertices);})
    .def("add_face",[](Surface_mesh&sm, Surface_mesh::Vertex_index &v0, Surface_mesh::Vertex_index &v1, Surface_mesh::Vertex_index &v2) {return sm.add_face(v0,v1,v2);})
    .def("add_face",[](Surface_mesh&sm, Surface_mesh::Vertex_index &v0, Surface_mesh::Vertex_index &v1, Surface_mesh::Vertex_index &v2, Surface_mesh::Vertex_index &v3) {return sm.add_face(v0,v1,v2,v3);})
    /* Memory management */
    .def("number_of_vertices",[](Surface_mesh &sm){return sm.number_of_vertices();})
    .def("number_of_halfedges",[](Surface_mesh &sm){return sm.number_of_halfedges();})
    .def("number_of_edges",[](Surface_mesh &sm){return sm.number_of_edges();})
    .def("number_of_faces",[](Surface_mesh &sm){return sm.number_of_faces();})
    .def("is_empty",[](Surface_mesh &sm){return sm.is_empty();})
    .def("clear_without_removing_property_maps",[](Surface_mesh &sm) {sm.clear_without_removing_property_maps();})
    .def("clear",[](Surface_mesh &sm) {sm.clear();});

    /* Validity checks */


  }
