#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Point_3 Point_EPICK;
typedef Kernel_EPICK::Vector_3 Vector_3_EPICK;
typedef CGAL::Aff_transformation_3<Kernel_EPICK> Aff_transformation_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Point_3 Point_EPECK;
typedef Kernel_EPECK::Vector_3 Vector_3_EPECK;
typedef CGAL::Aff_transformation_3<Kernel_EPECK> Aff_transformation_3_EPECK;

#include <CGAL/aff_transformation_tags.h>

PYBIND11_MODULE(Aff_transformation_3, m) {

  py::class_<Aff_transformation_3_EPICK>(m, "Aff_transformation_3_EPICK")
      /* Creation */
      .def(py::init<const CGAL::Identity_transformation &>())
      .def(py::init<const CGAL::Translation &, const Vector_3_EPICK &>())
      .def(py::init<const CGAL::Scaling &, const Kernel_EPICK::RT &,
                    const Kernel_EPICK::RT &>())
      .def(py::init<const CGAL::Scaling &, const double &, const double &>())
      .def(py::init<const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT>())
      .def(py::init<const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double>())
      .def(py::init<const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT>())
      .def(py::init<const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double, const double>())

      /* Operations */
      .def("transform",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Point_3 &p) { return t.transform(p); })
      .def("transform",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Vector_3 &v) { return t.transform(v); })
      .def("transform",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Direction_3 &d) { return t.transform(d); })
      .def("transform",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Plane_3 &p) { return t.transform(p); })
      .def("__call__",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Point_3 &p) { return t.transform(p); })
      .def("__call__",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Vector_3 &v) { return t.transform(v); })
      .def("__call__",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Direction_3 &d) { return t.transform(d); })
      .def("__call__",
           [](const Aff_transformation_3_EPICK &t,
              const Kernel_EPICK::Plane_3 &p) { return t.transform(p); })
      .def("__mul__",
           [](const Aff_transformation_3_EPICK &t1,
              const Aff_transformation_3_EPICK &t2) { return t1 * t2; })
      .def("inverse", &Aff_transformation_3_EPICK::inverse)
      .def("__eq__",
           [](const Aff_transformation_3_EPICK &t1,
              const Aff_transformation_3_EPICK &t2) { return t1 == t2; })
      .def("is_even", &Aff_transformation_3_EPICK::is_even)
      .def("is_odd", &Aff_transformation_3_EPICK::is_odd)
      .def("is_scaling", &Aff_transformation_3_EPICK::is_scaling)
      .def("is_translation", &Aff_transformation_3_EPICK::is_translation)

      /* Matrix Entry Access */
      .def("cartesian", &Aff_transformation_3_EPICK::cartesian)
      .def("m", &Aff_transformation_3_EPICK::m)
      .def("m", &Aff_transformation_3_EPICK::homogeneous)
      .def("hm", &Aff_transformation_3_EPICK::hm);

  py::class_<Aff_transformation_3_EPECK>(m, "Aff_transformation_3_EPECK")
      /* Creation */
      .def(py::init<const CGAL::Identity_transformation &>())
      .def(py::init<const CGAL::Translation &, const Vector_3_EPECK &>())
      .def(py::init<const CGAL::Scaling &, const Kernel_EPECK::RT &,
                    const Kernel_EPECK::RT &>())
      .def(py::init<const CGAL::Scaling &, const double &, const double &>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT>())
      .def(py::init<const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT>())
      .def(py::init<const double, const double, const double, const double,
                    const double, const double, const double, const double,
                    const double, const double>())

      /* Operations */
      .def("transform",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Point_3 &p) { return t.transform(p); })
      .def("transform",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Vector_3 &v) { return t.transform(v); })
      .def("transform",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Direction_3 &d) { return t.transform(d); })
      .def("transform",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Plane_3 &p) { return t.transform(p); })
      .def("__call__",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Point_3 &p) { return t.transform(p); })
      .def("__call__",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Vector_3 &v) { return t.transform(v); })
      .def("__call__",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Direction_3 &d) { return t.transform(d); })
      .def("__call__",
           [](const Aff_transformation_3_EPECK &t,
              const Kernel_EPECK::Plane_3 &p) { return t.transform(p); })
      .def("__mul__",
           [](const Aff_transformation_3_EPECK &t1,
              const Aff_transformation_3_EPECK &t2) { return t1 * t2; })
      .def("inverse", &Aff_transformation_3_EPECK::inverse)
      .def("__eq__",
           [](const Aff_transformation_3_EPECK &t1,
              const Aff_transformation_3_EPECK &t2) { return t1 == t2; })
      .def("is_even", &Aff_transformation_3_EPECK::is_even)
      .def("is_odd", &Aff_transformation_3_EPECK::is_odd)
      .def("is_scaling", &Aff_transformation_3_EPECK::is_scaling)
      .def("is_translation", &Aff_transformation_3_EPECK::is_translation)

      /* Matrix Entry Access */
      .def("cartesian", &Aff_transformation_3_EPECK::cartesian)
      .def("m", &Aff_transformation_3_EPECK::m)
      .def("m", &Aff_transformation_3_EPECK::homogeneous)
      .def("hm", &Aff_transformation_3_EPECK::hm);

  /* pbind11 only */
  // TODO
}
