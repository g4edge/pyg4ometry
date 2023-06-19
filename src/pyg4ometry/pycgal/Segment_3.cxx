#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Segment_3 Segment_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Segment_3 Segment_3_EPECK;

PYBIND11_MODULE(Segment_3, m) {
  py::class_<Segment_3_EPICK>(m, "Segment_3_EPICK");
  py::class_<Segment_3_EPECK>(m, "Segment_3_EPECK");
}
