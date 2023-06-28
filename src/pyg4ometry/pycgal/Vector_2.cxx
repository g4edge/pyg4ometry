#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Vector_2 Vector_2_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Vector_2 Vector_2_EPECK;

PYBIND11_MODULE(Vector_2, m) {
  py::class_<Vector_2_EPICK>(m, "Vector_2_EPICK")
      .def(py::init<>())
      .def(py::init<int, int>())
      .def(py::init<double, double>())
      .def("x", [](Vector_2_EPICK &p2) { return CGAL::to_double(p2.x()); })
      .def("y", [](Vector_2_EPICK &p2) { return CGAL::to_double(p2.y()); });

  py::class_<Vector_2_EPECK>(m, "Vector_2_EPECK")
      .def(py::init<>())
      .def(py::init<int, int>())
      .def(py::init<double, double>())
      .def("x", [](Vector_2_EPECK &p2) { return CGAL::to_double(p2.x()); })
      .def("y", [](Vector_2_EPECK &p2) { return CGAL::to_double(p2.y()); });
}
