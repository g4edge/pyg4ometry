#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef Kernel_EPICK::Iso_cuboid_3                            Iso_cuboid_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef Kernel_EPECK::Iso_cuboid_3                            Iso_cuboid_3_EPECK;

PYBIND11_MODULE(Iso_cuboid_3, m) {
  py::class_<Iso_cuboid_3_EPICK>(m,"Iso_cuboid_3_EPICK");

  py::class_<Iso_cuboid_3_EPECK>(m,"Iso_cuboid_3_EPECK")
  /* related functions */
    .def("__eq__",[](const Iso_cuboid_3_EPECK &c1, const Iso_cuboid_3_EPECK &c2) {return c1 == c2;})
    .def("__ne__",[](const Iso_cuboid_3_EPECK &c1, const Iso_cuboid_3_EPECK &c2) {return c1 != c2;})

  /* creation */
    .def(py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &>())
    .def(py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &, int>())
    .def(py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &,
                  const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &,
                  const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &>())
    .def(py::init<const Kernel_EPECK::RT &, const Kernel_EPECK::RT &, const Kernel_EPECK::RT &,
                  const Kernel_EPECK::RT &, const Kernel_EPECK::RT &, const Kernel_EPECK::RT &,
                  const Kernel_EPECK::RT &>())
    .def(py::init<const double &, const double &, const double &,
                  const double &, const double &, const double &,
                  const double &>())
    .def(py::init<const CGAL::Bbox_3 &>())

  /* Operations */

  /* predicates */

  /* Miscellaneous */
    .def("bbox",[](const Iso_cuboid_3_EPECK &c) {return c.bbox();});
}