#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                 Point_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                 Point_3_EPECK;

PYBIND11_MODULE(Point_3, m) {
  py::class_<Point_3_EPICK>(m,"Point_3_EPICK")
    .def(py::init<>())
    .def(py::init<int, int, int>())
    .def(py::init<double,double,double>())
    .def("x",[](Point_3_EPICK &p3) {return CGAL::to_double(p3.x());})
    .def("y",[](Point_3_EPICK &p3) {return CGAL::to_double(p3.y());})
    .def("z",[](Point_3_EPICK &p3) {return CGAL::to_double(p3.z());});

  py::class_<Point_3_EPECK>(m,"Point_3_EPECK")
    .def(py::init<>())
    .def(py::init<int, int, int>())
    .def(py::init<double,double,double>())
    .def("x",[](Point_3_EPECK &p3) {return CGAL::to_double(p3.x());})
    .def("y",[](Point_3_EPECK &p3) {return CGAL::to_double(p3.y());})
    .def("z",[](Point_3_EPECK &p3) {return CGAL::to_double(p3.z());});
}