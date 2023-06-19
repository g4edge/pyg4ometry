#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Circle_3 Circle_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Circle_3 Circle_3_EPECK;

PYBIND11_MODULE(Circle_3, m) {

  py::class_<Circle_3_EPICK>(m, "Circle_3_EPICK")
      /* related functions */
      .def("__eq__", [](const Circle_3_EPICK &c1,
                        const Circle_3_EPICK &c2) { return c1 == c2; })
      .def("__ne__", [](const Circle_3_EPICK &c1,
                        const Circle_3_EPICK &c2) { return c1 != c2; })

      /* Creation */
      .def(py::init<const Kernel_EPICK::Point_3 &, const Kernel_EPICK::FT &,
                    const Kernel_EPICK::Plane_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &, const double &,
                    const Kernel_EPICK::Plane_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &, const Kernel_EPICK::FT &,
                    const Kernel_EPICK::Vector_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &, const double &,
                    const Kernel_EPICK::Vector_3 &>())
      .def(py::init<const Kernel_EPICK::Sphere_3 &,
                    const Kernel_EPICK::Sphere_3 &>())
      .def(py::init<const Kernel_EPICK::Sphere_3 &,
                    const Kernel_EPICK::Plane_3 &>())
      .def(py::init<const Kernel_EPICK::Plane_3 &,
                    const Kernel_EPICK::Sphere_3 &>())

      /* Access functions */
      .def("center", &Circle_3_EPICK::center)
      .def("squared_radius", &Circle_3_EPICK::squared_radius)
      .def("supporting_plane", &Circle_3_EPICK::supporting_plane)
      .def("diametral_sphere", &Circle_3_EPICK::diametral_sphere)
      .def("area_divided_by_pi", &Circle_3_EPICK::area_divided_by_pi)
      .def("approximate_area", &Circle_3_EPICK::approximate_area)
      .def("squared_length_divided_by_pi_square",
           &Circle_3_EPICK::squared_length_divided_by_pi_square)
      .def("approximate_squared_length",
           &Circle_3_EPICK::approximate_squared_length)

      /* Predicates */
      .def("had_on", &Circle_3_EPICK::has_on)

      /* Operations */
      .def("bbox", [](const Circle_3_EPICK &c) { return c.bbox(); });

  py::class_<Circle_3_EPECK>(m, "Circle_3_EPECK")
      /* related functions */
      .def("__eq__", [](const Circle_3_EPECK &c1,
                        const Circle_3_EPECK &c2) { return c1 == c2; })
      .def("__ne__", [](const Circle_3_EPECK &c1,
                        const Circle_3_EPECK &c2) { return c1 != c2; })

      /* Creation */
      .def(py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::FT &,
                    const Kernel_EPECK::Plane_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &, const double &,
                    const Kernel_EPECK::Plane_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::FT &,
                    const Kernel_EPECK::Vector_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &, const double &,
                    const Kernel_EPECK::Vector_3 &>())
      .def(py::init<const Kernel_EPECK::Sphere_3 &,
                    const Kernel_EPECK::Sphere_3 &>())
      .def(py::init<const Kernel_EPECK::Sphere_3 &,
                    const Kernel_EPECK::Plane_3 &>())
      .def(py::init<const Kernel_EPECK::Plane_3 &,
                    const Kernel_EPECK::Sphere_3 &>())

      /* Access functions */
      .def("center", &Circle_3_EPECK::center)
      .def("squared_radius", &Circle_3_EPECK::squared_radius)
      .def("supporting_plane", &Circle_3_EPECK::supporting_plane)
      .def("diametral_sphere", &Circle_3_EPECK::diametral_sphere)
      .def("area_divided_by_pi", &Circle_3_EPECK::area_divided_by_pi)
      .def("approximate_area", &Circle_3_EPECK::approximate_area)
      .def("squared_length_divided_by_pi_square",
           &Circle_3_EPECK::squared_length_divided_by_pi_square)
      .def("approximate_squared_length",
           &Circle_3_EPECK::approximate_squared_length)

      /* Predicates */
      .def("had_on", &Circle_3_EPECK::has_on)

      /* Operations */
      .def("bbox", [](const Circle_3_EPECK &c) { return c.bbox(); });

  /* pbind11 only */
  // TODO
}
