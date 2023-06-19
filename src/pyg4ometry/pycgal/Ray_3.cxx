#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Ray_3 Ray_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Ray_3 Ray_3_EPECK;

PYBIND11_MODULE(Ray_3, m) {
  py::class_<Ray_3_EPICK>(m, "Ray_3_EPICK")
      /* Creation */
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Point_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Direction_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Vector_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Line_3 &>())

      /* Operations */
      .def("__eq__", [](const Ray_3_EPICK &r1,
                        const Ray_3_EPICK &r2) { return r1 == r2; })
      .def("__ne__", [](const Ray_3_EPICK &r1,
                        const Ray_3_EPICK &r2) { return r1 != r2; })
      .def("source", &Ray_3_EPICK::source)
      .def("point", &Ray_3_EPICK::point)
      .def("direction", &Ray_3_EPICK::direction)
      .def("to_vector", &Ray_3_EPICK::to_vector)
      .def("supporting_line", &Ray_3_EPICK::supporting_line)
      .def("opposite", &Ray_3_EPICK::opposite)
      .def("is_degenerate", &Ray_3_EPICK::is_degenerate)
      .def("has_on", &Ray_3_EPICK::has_on)
      .def("transform", &Ray_3_EPICK::transform);

  py::class_<Ray_3_EPECK>(m, "Ray_3_EPECK")
      /* Creation */
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Point_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Direction_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Vector_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Line_3 &>())

      /* Operations */
      .def("__eq__", [](const Ray_3_EPECK &r1,
                        const Ray_3_EPECK &r2) { return r1 == r2; })
      .def("__ne__", [](const Ray_3_EPECK &r1,
                        const Ray_3_EPECK &r2) { return r1 != r2; })
      .def("source", &Ray_3_EPECK::source)
      .def("point", &Ray_3_EPECK::point)
      .def("direction", &Ray_3_EPECK::direction)
      .def("to_vector", &Ray_3_EPECK::to_vector)
      .def("supporting_line", &Ray_3_EPECK::supporting_line)
      .def("opposite", &Ray_3_EPECK::opposite)
      .def("is_degenerate", &Ray_3_EPECK::is_degenerate)
      .def("has_on", &Ray_3_EPECK::has_on)
      .def("transform", &Ray_3_EPECK::transform);
}
