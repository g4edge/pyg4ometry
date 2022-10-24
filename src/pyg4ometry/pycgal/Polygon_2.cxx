#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/partition_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef CGAL::Partition_traits_2<Kernel_EPICK>              Partition_traits_2_EPICK;
typedef Partition_traits_2_EPICK::Point_2                   Point_2_EPICK;
typedef Partition_traits_2_EPICK::Polygon_2                 Polygon_2_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel   Kernel_EPECK;
typedef CGAL::Partition_traits_2<Kernel_EPECK>              Partition_traits_2_EPECK;
typedef Partition_traits_2_EPECK::Point_2                   Point_2_EPECK;
typedef Partition_traits_2_EPECK::Polygon_2                 Polygon_2_EPECK;

PYBIND11_MAKE_OPAQUE(std::vector<Polygon_2_EPICK>);
PYBIND11_MAKE_OPAQUE(std::vector<Polygon_2_EPECK>);

PYBIND11_MODULE(Polygon_2, m) {

  py::class_<Polygon_2_EPICK>(m,"Polygon_2_EPICK")
    .def(py::init<>())
    .def("size",&Polygon_2_EPICK::size)
    .def("push_back",&Polygon_2_EPICK::push_back)

    /* Random access methods */
    .def("vertex",[](Polygon_2_EPICK &pg, std::size_t i) {return pg.vertex(i);});


  py::bind_vector<std::vector<Polygon_2_EPICK>>(m, "List_Polygon_2_EPICK");

  py::class_<Polygon_2_EPECK>(m,"Polygon_2_EPECK")
    .def(py::init<>())
    .def("size",&Polygon_2_EPECK::size)
    .def("push_back",&Polygon_2_EPECK::push_back)

    /* Random access methods */
    .def("vertex",[](Polygon_2_EPECK &pg, std::size_t i) {return pg.vertex(i);});
    ;

  py::bind_vector<std::vector<Polygon_2_EPECK>>(m, "List_Polygon_2_EPECK");

  m.def("test",[](Polygon_2_EPECK &polygon, std::vector<Polygon_2_EPECK> &partition_polys)
  {
    std::list<Polygon_2_EPECK> pp;

    CGAL::optimal_convex_partition_2(polygon.vertices_begin(),
	      			                 polygon.vertices_end(),
				                     std::back_inserter(partition_polys));
  });
}