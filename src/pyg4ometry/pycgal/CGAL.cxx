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

#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>

PYBIND11_MODULE(CGAL, m) {
   m.def("is_closed",[](Surface_mesh &pm) { return CGAL::is_closed(pm);},"Is the surface closed", py::arg("Surface_mesh"));
}