#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Triangle_3 Triangle_3_EPICK;
typedef Kernel_EPICK::Point_3 Point_3_EPICK;
typedef CGAL::Aff_transformation_3<Kernel_EPICK> Aff_transformation_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Triangle_3 Triangle_3_EPECK;
typedef Kernel_EPECK::Point_3 Point_3_EPECK;
typedef CGAL::Aff_transformation_3<Kernel_EPECK> Aff_transformation_3_EPECK;

PYBIND11_MODULE(Triangle_3, m) {
  py::class_<Triangle_3_EPICK>(m, "Triangle_3_EPICK")

      /* Creation */
      .def(py::init<Point_3_EPICK, Point_3_EPICK, Point_3_EPICK>())

      /* Operations */
      .def("__eq__",
           [](Triangle_3_EPICK &t1, Triangle_3_EPICK &t2) { return t1 == t2; })
      .def("__ne__",
           [](Triangle_3_EPICK &t1, Triangle_3_EPICK &t2) { return t1 != t2; })
      .def("vertex", &Triangle_3_EPICK::vertex)
      .def("__getitem__", [](Triangle_3_EPICK &t, int i) { return t[i]; })
      .def("supporting_plane", &Triangle_3_EPICK::supporting_plane)

      /* Predicates */
      .def("is_degenerate", &Triangle_3_EPICK::is_degenerate)
      .def("has_on", &Triangle_3_EPICK::has_on)

      /* Miscellaneous */
      .def("squared_area", &Triangle_3_EPICK::squared_area)
      .def("bbox", &Triangle_3_EPICK::bbox)
      .def("transform", &Triangle_3_EPICK::transform);

  py::class_<Triangle_3_EPECK>(m, "Triangle_3_EPECK")

      /* Creation */
      .def(py::init<Point_3_EPECK, Point_3_EPECK, Point_3_EPECK>())

      /* Operations */
      .def("__eq__",
           [](Triangle_3_EPECK &t1, Triangle_3_EPECK &t2) { return t1 == t2; })
      .def("__ne__",
           [](Triangle_3_EPECK &t1, Triangle_3_EPECK &t2) { return t1 != t2; })
      .def("vertex", &Triangle_3_EPECK::vertex)
      .def("__getitem__", [](Triangle_3_EPECK &t, int i) { return t[i]; })
      .def("supporting_plane", &Triangle_3_EPECK::supporting_plane)

      /* Predicates */
      .def("is_degenerate", &Triangle_3_EPECK::is_degenerate)
      .def("has_on", &Triangle_3_EPECK::has_on)

      /* Miscellaneous */
      .def("squared_area", &Triangle_3_EPECK::squared_area)
      .def("bbox", &Triangle_3_EPECK::bbox)
      .def("transform", &Triangle_3_EPECK::transform);
}
