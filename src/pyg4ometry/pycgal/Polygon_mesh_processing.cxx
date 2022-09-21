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

#include <CGAL/Aff_transformation_3.h>

typedef CGAL::Aff_transformation_3<Kernel>                    Aff_transformation_3;

#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/transform.h>

PYBIND11_MODULE(Polygon_mesh_processing, m) {
   m.doc() = "CGAL Polygon mesh processing";
   m.def("reverse_face_orientations",[](Surface_mesh &pm){ CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);},"Reverse all face orientations", py::arg("Surface_mesh"));
   m.def("transform",[](Aff_transformation_3 &transl, Surface_mesh &sm){CGAL::Polygon_mesh_processing::transform(transl,sm);});
   m.def("corefine_and_compute_union",[](Surface_mesh &pm1, Surface_mesh &pm2, Surface_mesh &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1,pm2,out);});
}