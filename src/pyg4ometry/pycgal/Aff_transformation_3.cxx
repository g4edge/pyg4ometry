#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                 Point_EPICK;
typedef Kernel_EPICK::Vector_3                                Vector_3_EPICK;
typedef CGAL::Aff_transformation_3<Kernel_EPICK>              Aff_transformation_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                 Point_EPECK;
typedef Kernel_EPECK::Vector_3                                Vector_3_EPECK;
typedef CGAL::Aff_transformation_3<Kernel_EPECK>              Aff_transformation_3_EPECK;

#include <CGAL/aff_transformation_tags.h>

PYBIND11_MODULE(Aff_transformation_3, m) {

  py::class_<Aff_transformation_3_EPICK>(m,"Aff_transformation_3_EPICK")
    .def(py::init<const CGAL::Identity_transformation &>())
    .def(py::init<const CGAL::Translation&, const Vector_3_EPICK &>())
    .def(py::init<double, double, double,
                  double, double, double,
                  double, double, double, double>());

  py::class_<Aff_transformation_3_EPECK>(m,"Aff_transformation_3_EPECK")
    .def(py::init<const CGAL::Identity_transformation &>())
    .def(py::init<const CGAL::Translation&, const Vector_3_EPECK &>())
    .def(py::init<double, double, double,
                  double, double, double,
                  double, double, double, double>());

}