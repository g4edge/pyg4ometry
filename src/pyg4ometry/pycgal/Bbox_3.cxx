#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Bbox_3 Bbox_3;

PYBIND11_MODULE(Bbox_3, m) {

  py::class_<Bbox_3>(m, "Bbox_3")
      /* Related Functions */
      // TODO bbox_3, do_overlap

      /* Creation */
      .def(py::init<>())
      .def(py::init<double, double, double, double, double, double>())

      /* Operations */
      .def("__eq__",
           [](const Bbox_3 &b1, const Bbox_3 &b2) { return b1 == b2; })
      .def("__ne__",
           [](const Bbox_3 &b1, const Bbox_3 &b2) { return b1 != b2; })
      .def("dimension", &Bbox_3::dimension)
      .def("xmin", &Bbox_3::xmin)
      .def("ymin", &Bbox_3::ymin)
      .def("zmin", &Bbox_3::zmin)
      .def("xmax", &Bbox_3::xmax)
      .def("ymax", &Bbox_3::ymax)
      .def("zmax", &Bbox_3::zmax)
      .def("min", &Bbox_3::min)
      .def("max", &Bbox_3::max)
      .def("__add__",
           [](const Bbox_3 &b1, const Bbox_3 &b2) { return b1 + b2; })
      .def("__iadd__",
           [](Bbox_3 &b1, const Bbox_3 &b2) {
             b1 += b2;
             return b1;
           })
      .def("dilate", &Bbox_3::dilate);

  /* pbind11 only */
  // TODO
}
