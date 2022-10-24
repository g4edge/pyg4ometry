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

/* 3D algorithms */
#include <CGAL/convex_decomposition_3.h> 

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
#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>

#include <CGAL/Polygon_mesh_processing/distance.h>
#include <CGAL/tags.h>

/* typedefs */
typedef CGAL::Exact_predicates_exact_constructions_kernel   Kernel;
typedef Kernel::Point_3                                     Point;
typedef Kernel::Vector_3                                    Vector_3;
typedef CGAL::Surface_mesh<Kernel::Point_3>                 Surface_mesh;
typedef CGAL::Polyhedron_3<Kernel>                          Polyhedron_3;
typedef Polyhedron_3::HalfedgeDS                            HalfedgeDS_3;

typedef CGAL::Nef_polyhedron_3<Kernel>                      Nef_polyhedron_3;
typedef CGAL::Aff_transformation_3<Kernel>                  Aff_transformation_3;

typedef CGAL::Partition_traits_2<Kernel>                    Partition_traits_2;
typedef Partition_traits_2::Point_2                         Point_2;
typedef Partition_traits_2::Polygon_2                       Polygon_2; 

#include <boost/function_output_iterator.hpp>
#include <fstream>
#include <vector>
typedef boost::graph_traits<Surface_mesh>::halfedge_descriptor halfedge_descriptor;
typedef boost::graph_traits<Surface_mesh>::edge_descriptor     edge_descriptor;

/* pybind */
namespace py = pybind11;

template <class HDS> class Build_Polygon_VertexFacet : public CGAL::Modifier_base<HDS> 
{  
 private: 
  std::vector<std::vector<double>> _vertices;
  std::vector<std::vector<int>>    _facets;
  
 public:
  Build_Polygon_VertexFacet(const std::vector<std::vector<double>> &vertices,
			    const std::vector<std::vector<int>>    &facets) {
    _vertices = vertices;
    _facets    = facets;
  }
  
  void operator()( HDS& hds) {
    // Postcondition: hds is a valid polyhedral surface.
    CGAL::Polyhedron_incremental_builder_3<HDS> B(hds, true);
    
    B.begin_surface(_vertices.size(), _facets.size(),0, CGAL::Polyhedron_incremental_builder_3<HDS>::RELATIVE_INDEXING);
    
    typedef typename HDS::Vertex   Vertex;
    typedef typename Vertex::Point Point;
    
    for(auto vert : _vertices) {
      B.add_vertex(Point(vert[0], vert[1], vert[2]));
    }
    
    for(auto facet : _facets) {      
      B.begin_facet();
      for(auto ivert : facet) {
	B.add_vertex_to_facet(ivert);	
      }
      B.end_facet();
    }
    B.end_surface();
  }
};   

class Polyhedron {
 public :
  Polyhedron_3 *_polyhedron; 

  Polyhedron();
  Polyhedron(const std::vector<std::vector<double>> &vertices, 
	     const std::vector<std::vector<int>>    &facets);
  Polyhedron(const py::list vertices, 
	     const py::list facets);
  Polyhedron(const py::array_t<double> vertices, 
	     const py::array_t<int> facets);
  ~Polyhedron();
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
  std::size_t add_face(const std::vector<unsigned int> &face);

  void translate(double x, double y, double z);
  void transform(double m11, double m12, double m13,
		 double m21, double m22, double m23,
		 double m31, double m32, double m33);

  SurfaceMesh* unioN(SurfaceMesh &);
  SurfaceMesh* intersect(SurfaceMesh &);
  SurfaceMesh* subtract(SurfaceMesh &);
  void         reverse_face_orientations();
  bool         is_valid();
  bool         is_outward_oriented();
  bool         is_closed();
  bool         does_self_intersect();
  bool         does_bound_a_volume();
  void         triangulate_faces();
  void         isotropic_remeshing();
  int          number_of_border_halfedges(bool verbose = false);

  py::list* toVerticesAndPolygons();
  int number_of_faces();
  int number_of_vertices();

  std::size_t hash();

  std::string toString();
};

double haussdorf_distance(SurfaceMesh &m1, SurfaceMesh &m2);
double symmetric_haussdorf_distance(SurfaceMesh &m1, SurfaceMesh &m2);

class NefPolyhedron {
 public:
  Nef_polyhedron_3 *_nef_polyhedron;

  NefPolyhedron(); 
  NefPolyhedron(const Polyhedron &polyhedron);
  NefPolyhedron(const SurfaceMesh &surfacemesh);
  NefPolyhedron(Nef_polyhedron_3 *nef_polyhedron);
  ~NefPolyhedron();
  std::vector<NefPolyhedron*> convexDecomposition(); 
  void print();
  int number_of_volumes();
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
