#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Line_3 Line_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Line_3 Line_3_EPECK;

PYBIND11_MODULE(Line_3, m) {
  py::class_<Line_3_EPICK>(m, "Line_3_EPICK")
      /* Creation */
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Point_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Direction_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Vector_3 &>())
      .def(py::init<const Kernel_EPICK::Segment_3 &>())
      .def(py::init<const Kernel_EPICK::Ray_3 &>())

      /* Operations */
      .def("__eq__", [](const Line_3_EPICK &l1,
                        const Line_3_EPICK &l2) { return l1 == l2; })
      .def("__ne__", [](const Line_3_EPICK &l1,
                        const Line_3_EPICK &l2) { return l1 != l2; })
      .def("projection", &Line_3_EPICK::projection)
      .def("point", [](const Line_3_EPICK &l1,
                       const Kernel_EPICK::FT i) { return l1.point(i); })
      .def("point",
           [](const Line_3_EPICK &l1, const double i) { return l1.point(i); })

      /* Predicates */
      .def("is_degenerate", &Line_3_EPICK::is_degenerate)
      .def("has_on", &Line_3_EPICK::has_on)

      /* Miscellaneous */
      .def("perpendicular_plane", &Line_3_EPICK::perpendicular_plane)
      .def("opposite", &Line_3_EPICK::opposite)
      .def("to_vector", &Line_3_EPICK::to_vector)
      .def("direction", &Line_3_EPICK::direction)
      .def("transform", &Line_3_EPICK::transform);

  py::class_<Line_3_EPECK>(m, "Line_3_EPECK")
      /* Creation */
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Point_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Direction_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Vector_3 &>())
      .def(py::init<const Kernel_EPECK::Segment_3 &>())
      .def(py::init<const Kernel_EPECK::Ray_3 &>())

      /* Operations */
      .def("__eq__", [](const Line_3_EPECK &l1,
                        const Line_3_EPECK &l2) { return l1 == l2; })
      .def("__ne__", [](const Line_3_EPECK &l1,
                        const Line_3_EPECK &l2) { return l1 != l2; })
      .def("projection", &Line_3_EPECK::projection)
      .def("point", [](const Line_3_EPECK &l1,
                       const Kernel_EPECK::FT i) { return l1.point(i); })
      .def("point",
           [](const Line_3_EPECK &l1, const double i) { return l1.point(i); })

      /* Predicates */
      .def("is_degenerate", &Line_3_EPECK::is_degenerate)
      .def("has_on", &Line_3_EPECK::has_on)

      /* Miscellaneous */
      .def("perpendicular_plane", &Line_3_EPECK::perpendicular_plane)
      .def("opposite", &Line_3_EPECK::opposite)
      .def("to_vector", &Line_3_EPECK::to_vector)
      .def("direction", &Line_3_EPECK::direction)
      .def("transform", &Line_3_EPECK::transform);
}
