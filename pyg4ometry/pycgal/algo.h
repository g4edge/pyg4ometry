#ifndef __ALGO_H
#define __ALGO_H 

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>

#include "geom.h"

/* Kernel */
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Simple_cartesian.h>

/* 3D objects */
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Surface_mesh.h>

/* 2D Objects */
#include <CGAL/Partition_traits_2.h>
#include <CGAL/number_utils.h>
#include <CGAL/boost/graph/iterator.h>

/* 2D Algorithms */
#include <CGAL/partition_2.h>

/* transformations */
#include <CGAL/Aff_transformation_3.h>
#include <CGAL/Polygon_mesh_processing/transform.h>
/* corefinement */
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel;
// typedef CGAL::Simple_cartesian<double>                      Kernel;
typedef Kernel::Point_3                                     Point;
typedef Kernel::Vector_3                                    Vector_3;
typedef CGAL::Surface_mesh<Kernel::Point_3>                 Surface_mesh;
typedef CGAL::Aff_transformation_3<Kernel>                  Aff_transformation_3;

typedef CGAL::Partition_traits_2<Kernel>                    Partition_traits_2;
typedef Partition_traits_2::Point_2                         Point_2;
typedef Partition_traits_2::Polygon_2                       Polygon_2; 

namespace py = pybind11;

class Polyhedron3 {
 public :
  Polyhedron3();
  ~Polyhedron3();
};

class NefPolyhedron3 {
 public:
  NefPolyhedron3();
  ~NefPolyhedron3();
};

class SurfaceMesh {
 public : 
  Surface_mesh* _surfacemesh;

  SurfaceMesh();
  SurfaceMesh(const SurfaceMesh &);
  SurfaceMesh(Surface_mesh *);
  SurfaceMesh(py::list vertices, py::list faces);
  SurfaceMesh(py::array_t<double>, py::array_t<int>);
  SurfaceMesh(std::string &fileName);
  ~SurfaceMesh();

  std::size_t add_vertex(double x, double y, double z);
  std::size_t add_face(std::size_t i, std::size_t j, std::size_t k);
  std::size_t add_face(std::size_t i, std::size_t j, std::size_t k, std::size_t l);

  void translate(double x, double y, double z);
  void transform(double m11, double m12, double m13,
		 double m21, double m22, double m23,
		 double m31, double m32, double m33);

  SurfaceMesh* unioN(SurfaceMesh &);
  SurfaceMesh* intersect(SurfaceMesh &);
  SurfaceMesh* subtract(SurfaceMesh &);
  bool         is_valid();
  bool         is_outward_oriented();
  bool         is_closed();
  bool         does_self_intersect();
  bool         does_bound_a_volume();
  void         triangulate_faces(); 

  py::list* toVerticesAndPolygons();
  int number_of_faces();

  std::string toString();
}; 

class Polygon2 {
 public :
  Polygon_2* _polygon;

  Polygon2();
  Polygon2(const Polygon2 &);
  Polygon2(const Polygon_2 &);
  Polygon2(py::list &p);
  Polygon2(py::list &x, py::list &y);
  Polygon2(py::array_t<double> &array);
  Polygon2(py::array_t<double> &x, py::array_t<double> &y);
  ~Polygon2();

  void push_back(double x, double y);
  void push_back(py::list &v);
  void push_back(py::array_t<double> &a);
  std::string toString() const;
  std::size_t size() const;
  void clear();
  void reverse_orientation();
  bool is_simple() const;
  bool is_convex() const;
  int  orientation() const;
  std::list<Polygon2> optimal_convex_partition();
};

#endif
