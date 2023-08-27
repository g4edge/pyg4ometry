#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_rational.h>
#include <CGAL/Extended_cartesian.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Plane_3 Plane_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Plane_3 Plane_3_EPECK;

typedef CGAL::Exact_rational ER;
typedef CGAL::Extended_cartesian<ER> Kernel_ECER;
typedef Kernel_ECER::Plane_3 Plane_3_ECER;

PYBIND11_MODULE(Plane_3, m) {
  py::class_<Plane_3_EPICK>(m, "Plane_3_EPICK")
      .def(py::init<const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT>())
      .def(py::init<const Kernel_EPICK::Point_3, const Kernel_EPICK::Point_3,
                    const Kernel_EPICK::Point_3>())
      .def(
          py::init<const Kernel_EPICK::Point_3, const Kernel_EPICK::Vector_3>())
      .def(py::init<const Kernel_EPICK::Point_3,
                    const Kernel_EPICK::Direction_3>())
      .def(py::init<const Kernel_EPICK::Line_3, const Kernel_EPICK::Point_3>())
      .def(py::init<const Kernel_EPICK::Ray_3, const Kernel_EPICK::Point_3>())
      .def(py::init<const Kernel_EPICK::Segment_3,
                    const Kernel_EPICK::Point_3>())
      .def(py::init<const Kernel_EPICK::Circle_3>())

      /* operations */
      .def("__eq__",
           [](Plane_3_EPICK &p1, const Plane_3_EPICK p2) { return p1 == p2; })
      .def("__ne__",
           [](Plane_3_EPICK &p1, const Plane_3_EPICK p2) { return p1 != p2; })
      .def("a", [](Plane_3_EPICK &p3) { return CGAL::to_double(p3.a()); })
      .def("b", [](Plane_3_EPICK &p3) { return CGAL::to_double(p3.b()); })
      .def("c", [](Plane_3_EPICK &p3) { return CGAL::to_double(p3.c()); })
      .def("d", [](Plane_3_EPICK &p3) { return CGAL::to_double(p3.d()); })
      .def("perpendicular_line", &Plane_3_EPICK::perpendicular_line)
      .def("projection", &Plane_3_EPICK::projection)
      .def("opposite", &Plane_3_EPICK::opposite)
      .def("point", &Plane_3_EPICK::point)
      .def("orthogonal_vector", &Plane_3_EPICK::orthogonal_vector)
      .def("orthogonal_direction", &Plane_3_EPICK::orthogonal_direction)
      .def("base1", &Plane_3_EPICK::base1)
      .def("base2", &Plane_3_EPICK::base2)

      /* 2d conversion */
      .def("to_2d", &Plane_3_EPICK::to_2d)
      .def("to_3d", &Plane_3_EPICK::to_3d)

      /* Predicates */
      .def("oriented_side", &Plane_3_EPICK::oriented_side)

      /* Convenience Boolean Functions */
      .def("has_on",
           [](const Plane_3_EPICK &pl, const Kernel_EPICK::Point_3 po) {
             return pl.has_on(po);
           })
      .def("has_on_positive_side", &Plane_3_EPICK::has_on_positive_side)
      .def("has_on_negative_side", &Plane_3_EPICK::has_on_negative_side)
      .def("has_on",
           [](const Plane_3_EPICK &pl, const Kernel_EPICK::Line_3 li) {
             return pl.has_on(li);
           })
      .def("has_on",
           [](const Plane_3_EPICK &pl, const Kernel_EPICK::Circle_3 ci) {
             return pl.has_on(ci);
           })
      .def("is_degenerate", &Plane_3_EPICK::is_degenerate)

      /* Miscellaneous */
      .def("transform", &Plane_3_EPICK::transform);

  py::class_<Plane_3_EPECK>(m, "Plane_3_EPECK")
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT>())
      .def(py::init<const Kernel_EPECK::Point_3, const Kernel_EPECK::Point_3,
                    const Kernel_EPECK::Point_3>())
      .def(
          py::init<const Kernel_EPECK::Point_3, const Kernel_EPECK::Vector_3>())
      .def(py::init<const Kernel_EPECK::Point_3,
                    const Kernel_EPECK::Direction_3>())
      .def(py::init<const Kernel_EPECK::Line_3, const Kernel_EPECK::Point_3>())
      .def(py::init<const Kernel_EPECK::Ray_3, const Kernel_EPECK::Point_3>())
      .def(py::init<const Kernel_EPECK::Segment_3,
                    const Kernel_EPECK::Point_3>())
      .def(py::init<const Kernel_EPECK::Circle_3>())

      /* operations */
      .def("__eq__",
           [](Plane_3_EPECK &p1, const Plane_3_EPECK p2) { return p1 == p2; })
      .def("__ne__",
           [](Plane_3_EPECK &p1, const Plane_3_EPECK p2) { return p1 != p2; })
      .def("a", [](Plane_3_EPECK &p3) { return CGAL::to_double(p3.a()); })
      .def("b", [](Plane_3_EPECK &p3) { return CGAL::to_double(p3.b()); })
      .def("c", [](Plane_3_EPECK &p3) { return CGAL::to_double(p3.c()); })
      .def("d", [](Plane_3_EPECK &p3) { return CGAL::to_double(p3.d()); })

      .def("perpendicular_line", &Plane_3_EPECK::perpendicular_line)
      .def("projection", &Plane_3_EPECK::projection)
      .def("opposite", &Plane_3_EPECK::opposite)
      .def("point", &Plane_3_EPECK::point)
      .def("orthogonal_vector", &Plane_3_EPECK::orthogonal_vector)
      .def("orthogonal_direction", &Plane_3_EPECK::orthogonal_direction)
      .def("base1", &Plane_3_EPECK::base1)
      .def("base2", &Plane_3_EPECK::base2)

      /* 2d conversion */
      .def("to_2d", &Plane_3_EPECK::to_2d)
      .def("to_3d", &Plane_3_EPECK::to_3d)

      /* Predicates */
      .def("oriented_side", &Plane_3_EPECK::oriented_side)

      /* Convenience Boolean Functions */
      .def("has_on",
           [](const Plane_3_EPECK &pl, const Kernel_EPECK::Point_3 po) {
             return pl.has_on(po);
           })
      .def("has_on_positive_side", &Plane_3_EPECK::has_on_positive_side)
      .def("has_on_negative_side", &Plane_3_EPECK::has_on_negative_side)
      .def("has_on",
           [](const Plane_3_EPECK &pl, const Kernel_EPECK::Line_3 li) {
             return pl.has_on(li);
           })
      .def("has_on",
           [](const Plane_3_EPECK &pl, const Kernel_EPECK::Circle_3 ci) {
             return pl.has_on(ci);
           })
      .def("is_degenerate", &Plane_3_EPECK::is_degenerate)

      /* Miscellaneous */
      .def("transform", &Plane_3_EPECK::transform);

  py::class_<Plane_3_ECER>(m, "Plane_3_ECER")
      .def(py::init<const Kernel_ECER::Point_3, const Kernel_ECER::Vector_3>());

  /* pybdind11 only */
}
