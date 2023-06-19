#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Iso_cuboid_3 Iso_cuboid_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Iso_cuboid_3 Iso_cuboid_3_EPECK;

PYBIND11_MODULE(Iso_cuboid_3, m) {
  py::class_<Iso_cuboid_3_EPICK>(m, "Iso_cuboid_3_EPICK")
      /* related functions */
      .def("__eq__", [](const Iso_cuboid_3_EPICK &c1,
                        const Iso_cuboid_3_EPICK &c2) { return c1 == c2; })
      .def("__ne__", [](const Iso_cuboid_3_EPICK &c1,
                        const Iso_cuboid_3_EPICK &c2) { return c1 != c2; })

      /* creation */
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Point_3 &>())
      .def(py::init<const Kernel_EPICK::Point_3 &,
                    const Kernel_EPICK::Point_3 &, int>())
      .def(
          py::init<const Kernel_EPICK::Point_3 &, const Kernel_EPICK::Point_3 &,
                   const Kernel_EPICK::Point_3 &, const Kernel_EPICK::Point_3 &,
                   const Kernel_EPICK::Point_3 &,
                   const Kernel_EPICK::Point_3 &>())
      .def(py::init<const Kernel_EPICK::RT &, const Kernel_EPICK::RT &,
                    const Kernel_EPICK::RT &, const Kernel_EPICK::RT &,
                    const Kernel_EPICK::RT &, const Kernel_EPICK::RT &,
                    const Kernel_EPICK::RT &>())
      .def(py::init<const double &, const double &, const double &,
                    const double &, const double &, const double &,
                    const double &>())
      .def(py::init<const CGAL::Bbox_3 &>())

      /* Operations */
      .def("__eq__", [](const Iso_cuboid_3_EPICK &c1,
                        const Iso_cuboid_3_EPICK &c2) { return c1 == c2; })
      .def("__ne__", [](const Iso_cuboid_3_EPICK &c1,
                        const Iso_cuboid_3_EPICK &c2) { return c1 != c2; })
      .def("vertex", &Iso_cuboid_3_EPICK::vertex)
      .def("__getitem__",
           [](const Iso_cuboid_3_EPICK &c1, const int i) { return c1[i]; })
      .def("min", &Iso_cuboid_3_EPICK::min)
      .def("max", &Iso_cuboid_3_EPICK::max)
      .def("xmin", &Iso_cuboid_3_EPICK::xmin)
      .def("ymin", &Iso_cuboid_3_EPICK::ymin)
      .def("zmin", &Iso_cuboid_3_EPICK::zmin)
      .def("xmax", &Iso_cuboid_3_EPICK::xmax)
      .def("ymax", &Iso_cuboid_3_EPICK::ymax)
      .def("zmax", &Iso_cuboid_3_EPICK::zmax)
      .def("min_coord", &Iso_cuboid_3_EPICK::min_coord)
      .def("max_coord", &Iso_cuboid_3_EPICK::max_coord)

      /* predicates */
      .def("is_degenerate", &Iso_cuboid_3_EPICK::is_degenerate)
      .def("bounded_side", &Iso_cuboid_3_EPICK::bounded_side)
      .def("has_on_boundary", &Iso_cuboid_3_EPICK::has_on_boundary)
      .def("has_on_bounded_side", &Iso_cuboid_3_EPICK::has_on_bounded_side)
      .def("has_on_unbounded_side", &Iso_cuboid_3_EPICK::has_on_unbounded_side)

      /* Miscellaneous */
      .def("volume", &Iso_cuboid_3_EPICK::volume)
      .def("bbox", [](const Iso_cuboid_3_EPICK &c) { return c.bbox(); })
      .def("transform", &Iso_cuboid_3_EPICK::transform);

  py::class_<Iso_cuboid_3_EPECK>(m, "Iso_cuboid_3_EPECK")
      /* related functions */
      .def("__eq__", [](const Iso_cuboid_3_EPECK &c1,
                        const Iso_cuboid_3_EPECK &c2) { return c1 == c2; })
      .def("__ne__", [](const Iso_cuboid_3_EPECK &c1,
                        const Iso_cuboid_3_EPECK &c2) { return c1 != c2; })

      /* creation */
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Point_3 &>())
      .def(py::init<const Kernel_EPECK::Point_3 &,
                    const Kernel_EPECK::Point_3 &, int>())
      .def(
          py::init<const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &,
                   const Kernel_EPECK::Point_3 &, const Kernel_EPECK::Point_3 &,
                   const Kernel_EPECK::Point_3 &,
                   const Kernel_EPECK::Point_3 &>())
      .def(py::init<const Kernel_EPECK::RT &, const Kernel_EPECK::RT &,
                    const Kernel_EPECK::RT &, const Kernel_EPECK::RT &,
                    const Kernel_EPECK::RT &, const Kernel_EPECK::RT &,
                    const Kernel_EPECK::RT &>())
      .def(py::init<const double &, const double &, const double &,
                    const double &, const double &, const double &,
                    const double &>())
      .def(py::init<const CGAL::Bbox_3 &>())

      /* Operations */
      .def("__eq__", [](const Iso_cuboid_3_EPECK &c1,
                        const Iso_cuboid_3_EPECK &c2) { return c1 == c2; })
      .def("__ne__", [](const Iso_cuboid_3_EPECK &c1,
                        const Iso_cuboid_3_EPECK &c2) { return c1 != c2; })
      .def("vertex", &Iso_cuboid_3_EPECK::vertex)
      .def("__getitem__",
           [](const Iso_cuboid_3_EPECK &c1, const int i) { return c1[i]; })
      .def("min", &Iso_cuboid_3_EPECK::min)
      .def("max", &Iso_cuboid_3_EPECK::max)
      .def("xmin", &Iso_cuboid_3_EPECK::xmin)
      .def("ymin", &Iso_cuboid_3_EPECK::ymin)
      .def("zmin", &Iso_cuboid_3_EPECK::zmin)
      .def("xmax", &Iso_cuboid_3_EPECK::xmax)
      .def("ymax", &Iso_cuboid_3_EPECK::ymax)
      .def("zmax", &Iso_cuboid_3_EPECK::zmax)
      .def("min_coord", &Iso_cuboid_3_EPECK::min_coord)
      .def("max_coord", &Iso_cuboid_3_EPECK::max_coord)

      /* predicates */
      .def("is_degenerate", &Iso_cuboid_3_EPECK::is_degenerate)
      .def("bounded_side", &Iso_cuboid_3_EPECK::bounded_side)
      .def("has_on_boundary", &Iso_cuboid_3_EPECK::has_on_boundary)
      .def("has_on_bounded_side", &Iso_cuboid_3_EPECK::has_on_bounded_side)
      .def("has_on_unbounded_side", &Iso_cuboid_3_EPECK::has_on_unbounded_side)

      /* Miscellaneous */
      .def("volume", &Iso_cuboid_3_EPECK::volume)
      .def("bbox", [](const Iso_cuboid_3_EPECK &c) { return c.bbox(); })
      .def("transform", &Iso_cuboid_3_EPECK::transform);
}
