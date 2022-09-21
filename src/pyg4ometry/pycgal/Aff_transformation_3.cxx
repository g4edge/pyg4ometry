#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel;
typedef Kernel::Point_3                                       Point;
typedef Kernel::Vector_3                                      Vector_3;
typedef CGAL::Aff_transformation_3<Kernel>                    Aff_transformation_3;

PYBIND11_MODULE(Aff_transformation_3, m) {
  py::class_<Aff_transformation_3>(m,"Aff_transformation_3")
    .def(py::init<>());
}