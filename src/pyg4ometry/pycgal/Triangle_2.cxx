#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Triangle_2 Triangle_2_EPICK;
typedef Kernel_EPICK::Point_2 Point_2_EPICK;
typedef CGAL::Aff_transformation_2<Kernel_EPICK> Aff_transformation_2_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Triangle_2 Triangle_2_EPECK;
typedef Kernel_EPECK::Point_2 Point_2_EPECK;
typedef CGAL::Aff_transformation_2<Kernel_EPECK> Aff_transformation_2_EPECK;

// TODO complete class
PYBIND11_MODULE(Triangle_2, m) {
  py::class_<Triangle_2_EPICK>(m, "Triangle_2_EPICK")
      .def("vertex", &Triangle_2_EPICK::vertex);
  py::class_<Triangle_2_EPECK>(m, "Triangle_2_EPECK")
      .def("vertex", &Triangle_2_EPECK::vertex);
}
