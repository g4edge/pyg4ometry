#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/Polygon_with_holes_2.h>
#include <CGAL/partition_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef CGAL::Point_2<Kernel_EPICK> Point_2_EPICK;
typedef CGAL::Polygon_2<Kernel_EPICK> Polygon_2_EPICK;
typedef CGAL::Polygon_with_holes_2<Kernel_EPICK> Polygon_with_holes_2_EPICK;
typedef CGAL::General_polygon_with_holes_2<Kernel_EPICK>
    General_polygon_with_holes_2_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef CGAL::Point_2<Kernel_EPECK> Point_2_EPECK;
typedef CGAL::Polygon_2<Kernel_EPECK> Polygon_2_EPECK;
typedef CGAL::Polygon_with_holes_2<Kernel_EPECK> Polygon_with_holes_2_EPECK;
typedef CGAL::General_polygon_with_holes_2<Kernel_EPICK>
    General_polygon_with_holes_2_EPECK;

PYBIND11_MAKE_OPAQUE(std::vector<Polygon_with_holes_2_EPICK>);
PYBIND11_MAKE_OPAQUE(std::vector<Polygon_with_holes_2_EPECK>);

PYBIND11_MODULE(Polygon_with_holes_2, m) {
  py::class_<Polygon_with_holes_2_EPICK>(m, "Polygon_with_holes_2_EPICK")
      .def(py::init<>())
      .def(py::init<const Polygon_2_EPICK &>())
      .def("add_hole", [](Polygon_with_holes_2_EPICK &ph,
                          Polygon_2_EPICK &pa) { return ph.add_hole(pa); })
      .def("outer_boundary",
           [](Polygon_with_holes_2_EPICK &p) { return p.outer_boundary(); })
      .def("holes", [](Polygon_with_holes_2_EPICK &p) { return p.holes(); });
  py::bind_vector<std::vector<Polygon_with_holes_2_EPICK>>(
      m, "List_Polygon_with_holes_2_EPICK");

  py::class_<Polygon_with_holes_2_EPECK>(m, "Polygon_with_holes_2_EPECK")
      .def(py::init<>())
      .def(py::init<const Polygon_2_EPECK &>())
      .def("add_hole", [](Polygon_with_holes_2_EPECK &ph,
                          Polygon_2_EPECK &pa) { return ph.add_hole(pa); })
      .def("outer_boundary",
           [](Polygon_with_holes_2_EPECK &p) { return p.outer_boundary(); })
      .def("holes", [](Polygon_with_holes_2_EPECK &p) { return p.holes(); });
  py::bind_vector<std::vector<Polygon_with_holes_2_EPECK>>(
      m, "List_Polygon_with_holes_2_EPECK");
}
