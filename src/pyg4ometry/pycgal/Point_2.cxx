#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/partition_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef CGAL::Partition_traits_2<Kernel_EPICK> Partition_traits_2_EPICK;
typedef Partition_traits_2_EPICK::Point_2 Partition_traits_2_Point_2_EPICK;
typedef Kernel_EPICK::Point_2 Point_2_EPICK;
typedef Kernel_EPICK::Vector_2 Vector_2_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef CGAL::Partition_traits_2<Kernel_EPECK> Partition_traits_2_EPECK;
typedef Partition_traits_2_EPECK::Point_2 Partition_traits_2_Point_2_EPECK;
typedef Kernel_EPECK::Point_2 Point_2_EPECK;
typedef Kernel_EPECK::Vector_2 Vector_2_EPECK;

PYBIND11_MODULE(Point_2, m) {

  py::class_<Point_2_EPICK>(m, "Point_2_EPICK")
      .def(py::init<>())
      .def(py::init<int, int>())
      .def(py::init<double, double>())

      /* Coordinate access */
      .def("x", [](Point_2_EPICK &p2) { return CGAL::to_double(p2.x()); })
      .def("y", [](Point_2_EPICK &p2) { return CGAL::to_double(p2.y()); })

      /* operations */
      .def("__add__",
           [](Point_2_EPICK &p1, Vector_2_EPICK &p2) { return p1 + p2; })
      .def("__sub__",
           [](Point_2_EPICK &p1, Vector_2_EPICK &p2) { return p1 - p2; });

  py::class_<Point_2_EPECK>(m, "Point_2_EPECK")
      .def(py::init<>())
      .def(py::init<int, int>())
      .def(py::init<double, double>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT>())
      .def(py::init<const Kernel_EPECK::Weighted_point_2>())

      /* Coordinate access */
      .def("x", [](Point_2_EPECK &p2) { return CGAL::to_double(p2.x()); })
      .def("y", [](Point_2_EPECK &p2) { return CGAL::to_double(p2.y()); })

      /* operations */
      .def("__add__",
           [](Point_2_EPECK &p1, Vector_2_EPECK &p2) { return p1 + p2; })
      .def("__sub__",
           [](Point_2_EPECK &p1, Vector_2_EPECK &p2) { return p1 - p2; });
}
