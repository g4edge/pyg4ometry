#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Nef_polyhedron_3.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel                              Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                                          Point_EPECK;
typedef Kernel_EPECK::Vector_3                                                         Vector_EPECK;
typedef CGAL::Polyhedron_3<Kernel_EPECK>                                               Polyhedron_3_EPECK;
typedef CGAL::Nef_polyhedron_3<Kernel_EPECK>                                           Nef_polyhedron_3_EPECK;
typedef Nef_polyhedron_3_EPECK::Volume_const_iterator                                  Nef_polyhedron_3_EPECK_Volume_iterator;
typedef Nef_polyhedron_3_EPECK::Shell_entry_const_iterator                             Nef_polyhedron_3_EPECK_Shell_entry_iterator;

typedef CGAL::Exact_predicates_inexact_constructions_kernel                            Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                                          Point_EPICK;
typedef Kernel_EPICK::Vector_3                                                         Vector_EPICK;
typedef CGAL::Polyhedron_3<Kernel_EPICK>                                               Polyhedron_3_EPICK;
typedef CGAL::Nef_polyhedron_3<Kernel_EPICK>                                           Nef_polyhedron_3_EPICK;
typedef Nef_polyhedron_3_EPICK::Volume_const_iterator                                  Nef_polyhedron_3_EPICK_Volume_iterator;
typedef Nef_polyhedron_3_EPICK::Shell_entry_const_iterator                             Nef_polyhedron_3_EPICK_Shell_entry_iterator;

PYBIND11_MODULE(Nef_polyhedron_3, m) {
  py::class_<Nef_polyhedron_3_EPECK>(m,"Nef_polyhedron_3_EPECK")
    .def(py::init<>())
    .def(py::init<Polyhedron_3_EPECK&>())
    /* Access Member Functions */
    .def("is_simple",&Nef_polyhedron_3_EPECK::is_simple)
    .def("is_valid",&Nef_polyhedron_3_EPECK::is_valid)
    .def("number_of_vertices",&Nef_polyhedron_3_EPECK::number_of_vertices)
    .def("number_of_halfedges",&Nef_polyhedron_3_EPECK::number_of_halfedges)
    .def("number_of_edges",&Nef_polyhedron_3_EPECK::number_of_edges)
    .def("number_of_halffacets",&Nef_polyhedron_3_EPECK::number_of_halffacets)
    .def("number_of_facets",&Nef_polyhedron_3_EPECK::number_of_facets)
    .def("number_of_volumes",&Nef_polyhedron_3_EPECK::number_of_volumes)
    .def("volume_begin", [](Nef_polyhedron_3_EPECK &np) { return np.volumes_begin();})
    .def("volume_end", [](Nef_polyhedron_3_EPECK &np) { return np.volumes_end();})
    /* Operations */
    .def("convert_to_polyhedron",[](Nef_polyhedron_3_EPECK &np, Polyhedron_3_EPECK &p) {np.convert_to_polyhedron(p);})
    .def("convert_inner_shell_to_polyhedron",[](Nef_polyhedron_3_EPECK &np, Nef_polyhedron_3_EPECK_Shell_entry_iterator &si, Polyhedron_3_EPECK &p) {np.convert_inner_shell_to_polyhedron(si,p);});

  py::class_<Nef_polyhedron_3_EPECK_Volume_iterator>(m,"Nef_polyhedron_3_EPECK_Volume_iterator")
    .def(py::init<>())
    .def("next",[](Nef_polyhedron_3_EPECK_Volume_iterator &i) {++i;}, py::return_value_policy::reference)
    .def("__ne__",[](Nef_polyhedron_3_EPECK_Volume_iterator i1, Nef_polyhedron_3_EPECK_Volume_iterator i2) {return i1 != i2;})
    .def("mark",[](Nef_polyhedron_3_EPECK_Volume_iterator &i) {return i->mark();})
    .def("shells_begin",[](Nef_polyhedron_3_EPECK_Volume_iterator &i) {return i->shells_begin();})
    .def("shells_end",[](Nef_polyhedron_3_EPECK_Volume_iterator &i) {return i->shells_end();});

  py::class_<Nef_polyhedron_3_EPECK_Shell_entry_iterator>(m,"Nef_polyhedron_3_EPECK_Shell_entry_iterator")
    .def(py::init<>())
    .def("next",[](Nef_polyhedron_3_EPECK_Shell_entry_iterator &i) {++i;}, py::return_value_policy::reference)
    .def("__ne__",[](Nef_polyhedron_3_EPECK_Shell_entry_iterator i1, Nef_polyhedron_3_EPECK_Shell_entry_iterator i2) {return i1 != i2;});

  py::class_<Nef_polyhedron_3_EPICK>(m,"Nef_polyhedron_3_EPICK")
    .def(py::init<>())
    .def(py::init<Polyhedron_3_EPICK&>())
    /* Access Member Functions */
    .def("is_simple",&Nef_polyhedron_3_EPICK::is_simple)
    .def("is_valid",&Nef_polyhedron_3_EPICK::is_valid)
    .def("number_of_vertices",&Nef_polyhedron_3_EPICK::number_of_vertices)
    .def("number_of_halfedges",&Nef_polyhedron_3_EPICK::number_of_halfedges)
    .def("number_of_edges",&Nef_polyhedron_3_EPICK::number_of_edges)
    .def("number_of_halffacets",&Nef_polyhedron_3_EPICK::number_of_halffacets)
    .def("number_of_facets",&Nef_polyhedron_3_EPICK::number_of_facets)
    .def("number_of_volumes",&Nef_polyhedron_3_EPICK::number_of_volumes)
    .def("volume_begin", [](Nef_polyhedron_3_EPICK &np) { return np.volumes_begin();})
    .def("volume_end", [](Nef_polyhedron_3_EPICK &np) { return np.volumes_end();})
    /* Operations */
    .def("convert_to_polyhedron",[](Nef_polyhedron_3_EPICK &np, Polyhedron_3_EPICK &p) {np.convert_to_polyhedron(p);});

  py::class_<Nef_polyhedron_3_EPICK_Volume_iterator>(m,"Nef_polyhedron_3_EPICK_Volume_iterator")
    .def(py::init<>())
    .def("next",[](Nef_polyhedron_3_EPICK_Volume_iterator &i) {++i;}, py::return_value_policy::reference)
    .def("__ne__",[](Nef_polyhedron_3_EPICK_Volume_iterator i1, Nef_polyhedron_3_EPICK_Volume_iterator i2) {return i1 != i2;})
    .def("mark",[](Nef_polyhedron_3_EPICK_Volume_iterator &i) {return i->mark();})
    .def("shells_begin",[](Nef_polyhedron_3_EPICK_Volume_iterator &i) {return i->shells_begin();})
    .def("shells_end",[](Nef_polyhedron_3_EPICK_Volume_iterator &i) {return i->shells_end();});

  py::class_<Nef_polyhedron_3_EPICK_Shell_entry_iterator>(m,"Nef_polyhedron_3_EPICK_Shell_entry_iterator")
    .def(py::init<>())
    .def("next",[](Nef_polyhedron_3_EPICK_Shell_entry_iterator &i) {++i;}, py::return_value_policy::reference)
    .def("__ne__",[](Nef_polyhedron_3_EPICK_Shell_entry_iterator i1, Nef_polyhedron_3_EPICK_Shell_entry_iterator i2) {return i1 != i2;});

}
