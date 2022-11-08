#include <fstream>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Polyhedral_mesh_domain_3.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/partition_2.h>
#include <CGAL/Polygon_with_holes_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef CGAL::Partition_traits_2<Kernel_EPICK>                Partition_traits_2_EPICK;
typedef Partition_traits_2_EPICK::Point_2                     Partition_traits_2_Point_2_EPICK;
typedef Partition_traits_2_EPICK::Polygon_2                   Partition_traits_2_Polygon_2_EPICK;
typedef Kernel_EPICK::Point_2                                 Point_2_EPICK;
typedef Kernel_EPICK::Point_3                                 Point_3_EPICK;
typedef Kernel_EPICK::Vector_3                                Vector_3_EPICK;
typedef CGAL::Polygon_2<Kernel_EPICK>                         Polygon_2_EPICK;
typedef CGAL::Polygon_with_holes_2<Kernel_EPICK>              Polygon_with_holes_2_EPICK;
typedef CGAL::Polyhedron_3<Kernel_EPICK>                      Polyhedron_3_EPICK;
typedef CGAL::Surface_mesh<Kernel_EPICK::Point_3>             Surface_mesh_EPICK;
typedef CGAL::Nef_polyhedron_3<Kernel_EPICK>                  Nef_polyhedron_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef CGAL::Partition_traits_2<Kernel_EPECK>                Partition_traits_2_EPECK;
typedef Partition_traits_2_EPECK::Point_2                     Partition_traits_2_Point_2_EPECK;
typedef Partition_traits_2_EPECK::Polygon_2                   Partition_traits_2_Polygon_2_EPECK;
typedef Kernel_EPECK::Point_2                                 Point_2_EPECK;
typedef Kernel_EPECK::Point_3                                 Point_3_EPECK;
typedef Kernel_EPECK::Vector_3                                Vector_3_EPECK;
typedef CGAL::Polygon_2<Kernel_EPECK>                         Polygon_2_EPECK;
typedef CGAL::Polygon_with_holes_2<Kernel_EPECK>              Polygon_with_holes_2_EPECK;
typedef CGAL::Polyhedron_3<Kernel_EPECK>                      Polyhedron_3_EPECK;
typedef CGAL::Surface_mesh<Kernel_EPECK::Point_3>             Surface_mesh_EPECK;
typedef CGAL::Nef_polyhedron_3<Kernel_EPECK>                  Nef_polyhedron_3_EPECK;

#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/aff_transformation_tags.h>
#include <CGAL/boost/graph/helpers.h>
#include <CGAL/convex_decomposition_3.h>

#include <CGAL/Polyhedral_mesh_domain_3.h>
#include <CGAL/Mesh_triangulation_3.h>
#include <CGAL/Mesh_complex_3_in_triangulation_3.h>
#include <CGAL/Mesh_criteria_3.h>
#include <CGAL/make_mesh_3.h>

#include <CGAL/Boolean_set_operations_2.h>

#include <CGAL/number_utils.h>

typedef CGAL::Polyhedral_mesh_domain_3<Polyhedron_3_EPECK,Kernel_EPECK>  Polyhedral_mesh_domain_3_EPECK;
typedef CGAL::Mesh_triangulation_3<Polyhedral_mesh_domain_3_EPECK,CGAL::Default,CGAL::Sequential_tag>::type Tr_EPECK;
typedef CGAL::Mesh_complex_3_in_triangulation_3<Tr_EPECK> Mesh_complex_3_in_triangulation_3_EPECK;
typedef CGAL::Mesh_criteria_3<Tr_EPECK> Mesh_criteria_3_EPECK;

typedef CGAL::Polyhedral_mesh_domain_3<Polyhedron_3_EPICK,Kernel_EPICK>  Polyhedral_mesh_domain_3_EPICK;
typedef CGAL::Mesh_triangulation_3<Polyhedral_mesh_domain_3_EPICK,CGAL::Default,CGAL::Sequential_tag>::type Tr_EPICK;
typedef CGAL::Mesh_complex_3_in_triangulation_3<Tr_EPICK> Mesh_complex_3_in_triangulation_3_EPICK;
typedef CGAL::Mesh_criteria_3<Tr_EPICK> Mesh_criteria_3_EPICK;

PYBIND11_MAKE_OPAQUE(std::vector<Polygon_with_holes_2_EPICK>);
PYBIND11_MAKE_OPAQUE(std::vector<Polygon_with_holes_2_EPECK>);

PYBIND11_MODULE(CGAL, m) {

  py::class_<Kernel_EPICK::RT>(m,"EPICK_NT");
  py::class_<Kernel_EPECK::RT>(m,"EPECK_NT");

  //py::class_<Kernel_EPECK::RT>(m,"EPECK_NT");

  /* Algebraic foundations */
  m.def("to_double",[](Kernel_EPICK::RT &rt){return CGAL::to_double(rt);});
  m.def("to_double",[](Kernel_EPICK::FT &ft){return CGAL::to_double(ft);});
  m.def("to_double",[](Kernel_EPECK::RT &rt){return CGAL::to_double(rt);});
  m.def("to_double",[](Kernel_EPECK::FT &ft){return CGAL::to_double(ft);});

  py::class_<CGAL::Translation>(m,"Translation")
    .def(py::init<>());
  py::class_<CGAL::Rotation>(m,"Rotation")
    .def(py::init<>());
  py::class_<CGAL::Scaling>(m,"Scaling")
    .def(py::init<>());
  py::class_<CGAL::Identity_transformation>(m,"Identity_transformation")
    .def(py::init<>());

  m.def("is_closed",[](Surface_mesh_EPICK &pm) { return CGAL::is_closed(pm);},"Is the surface closed", py::arg("Surface_mesh_EPICK"));
  m.def("is_closed",[](Surface_mesh_EPECK &pm) { return CGAL::is_closed(pm);},"Is the surface closed", py::arg("Surface_mesh_EPECK"));

  /* Iterators and circulators */
  m.def("halfedges_around_face",[](Surface_mesh_EPECK::Halfedge_index &hi, Surface_mesh_EPECK &pm) {
    auto it = CGAL::halfedges_around_face(hi,pm);
    return py::make_iterator(it.begin(), it.end());
  },py::keep_alive<0, 1>());

  /* Boost graph library */

  /* Helper functions */
  m.def("clear",[](Polyhedron_3_EPECK &p) {CGAL::clear(p);});
  m.def("clear",[](Polyhedron_3_EPICK &p) {CGAL::clear(p);});
  m.def("clear",[](Surface_mesh_EPECK &p) {CGAL::clear(p);});
  m.def("clear",[](Surface_mesh_EPICK &p) {CGAL::clear(p);});
  m.def("copy_face_graph",[](Polyhedron_3_EPECK &p, Surface_mesh_EPECK &sm) {return CGAL::copy_face_graph(p,sm);});
  m.def("copy_face_graph",[](Polyhedron_3_EPICK &p, Surface_mesh_EPICK &sm) {return CGAL::copy_face_graph(p,sm);});
  m.def("copy_face_graph",[](Surface_mesh_EPECK &sm, Polyhedron_3_EPECK &p) {return CGAL::copy_face_graph(sm,p);});
  m.def("copy_face_graph",[](Surface_mesh_EPICK &sm, Polyhedron_3_EPICK &p) {return CGAL::copy_face_graph(sm,p);});
  m.def("copy_face_graph",[](Surface_mesh_EPICK &sm1, Surface_mesh_EPECK &sm2) {return CGAL::copy_face_graph(sm1,sm2);});
  m.def("copy_face_graph",[](Surface_mesh_EPECK &sm1, Surface_mesh_EPICK &sm2) {return CGAL::copy_face_graph(sm1,sm2);});
  m.def("copy_face_graph",[](Polyhedron_3_EPICK &p1, Polyhedron_3_EPECK &p2) {return CGAL::copy_face_graph(p1,p2);});
  m.def("copy_face_graph",[](Polyhedron_3_EPECK &p1, Polyhedron_3_EPICK &p2) {return CGAL::copy_face_graph(p1,p2);});

  /* 2D boolean */
  m.def("do_intersect",[](Polygon_2_EPECK &p1, Polygon_2_EPECK &p2) {return CGAL::do_intersect(p1,p2);});
  m.def("do_intersect",[](Polygon_2_EPICK &p1, Polygon_2_EPICK &p2) {return CGAL::do_intersect(p1,p2);});
  m.def("join",[](Polygon_2_EPICK &p1, Polygon_2_EPICK &p2, Polygon_with_holes_2_EPICK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_2_EPECK &p1, Polygon_2_EPECK &p2, Polygon_with_holes_2_EPECK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_with_holes_2_EPICK &p1, Polygon_2_EPICK &p2, Polygon_with_holes_2_EPICK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_with_holes_2_EPECK &p1, Polygon_2_EPECK &p2, Polygon_with_holes_2_EPECK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_2_EPICK &p1, Polygon_with_holes_2_EPICK &p2, Polygon_with_holes_2_EPICK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_2_EPECK &p1, Polygon_with_holes_2_EPECK &p2, Polygon_with_holes_2_EPECK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_with_holes_2_EPICK &p1, Polygon_with_holes_2_EPICK &p2, Polygon_with_holes_2_EPICK &pr) {
    CGAL::join(p1,p2,pr);
  });
  m.def("join",[](Polygon_with_holes_2_EPECK &p1, Polygon_with_holes_2_EPECK &p2, Polygon_with_holes_2_EPECK &pr) {
    CGAL::join(p1,p2,pr);
  });

  m.def("intersection",[](Polygon_2_EPICK &p1,Polygon_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });
  m.def("intersection",[](Polygon_2_EPECK &p1,Polygon_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });

  m.def("intersection",[](Polygon_with_holes_2_EPICK &p1,Polygon_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });
  m.def("intersection",[](Polygon_with_holes_2_EPECK &p1,Polygon_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });

  m.def("intersection",[](Polygon_2_EPICK &p1,Polygon_with_holes_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });
  m.def("intersection",[](Polygon_2_EPECK &p1,Polygon_with_holes_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });

  m.def("intersection",[](Polygon_with_holes_2_EPICK &p1,Polygon_with_holes_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });
  m.def("intersection",[](Polygon_with_holes_2_EPECK &p1,Polygon_with_holes_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &inter)
  {
    CGAL::intersection(p1,p2,std::back_inserter(inter));
  });

  m.def("difference",[](Polygon_2_EPICK &p1,Polygon_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });
  m.def("difference",[](Polygon_2_EPECK &p1,Polygon_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });

  m.def("difference",[](Polygon_with_holes_2_EPICK &p1,Polygon_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });
  m.def("difference",[](Polygon_with_holes_2_EPECK &p1,Polygon_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });

  m.def("difference",[](Polygon_2_EPICK &p1,Polygon_with_holes_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });
  m.def("difference",[](Polygon_2_EPECK &p1,Polygon_with_holes_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });

  m.def("difference",[](Polygon_with_holes_2_EPICK &p1,Polygon_with_holes_2_EPICK &p2, std::vector<Polygon_with_holes_2_EPICK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });
  m.def("difference",[](Polygon_with_holes_2_EPECK &p1,Polygon_with_holes_2_EPECK &p2, std::vector<Polygon_with_holes_2_EPECK> &diff)
  {
    CGAL::difference(p1,p2,std::back_inserter(diff));
  });

  /* TODO Boolean operations on Nef polyhedra */

  /* convex decomposition of nef polyhedra */
  m.def("convex_decomposition_3",[](Nef_polyhedron_3_EPICK &np) {CGAL::convex_decomposition_3(np);},py::return_value_policy::reference);
  m.def("convex_decomposition_3",[](Nef_polyhedron_3_EPECK &np) {CGAL::convex_decomposition_3(np);},py::return_value_policy::reference);

  /* 3d mesh generation */
  py::class_<Polyhedral_mesh_domain_3_EPICK>(m,"Polyhedral_mesh_domain_3_EPICK")
    .def(py::init<Polyhedron_3_EPICK &>());
  py::class_<Mesh_criteria_3_EPICK>(m,"Mesh_criteria_3_EPICK")
    .def(py::init<double,double,double,double,double>());
  py::class_<Mesh_complex_3_in_triangulation_3_EPICK>(m,"Mesh_complex_3_in_triangulation_3_EPICK")
    .def("output_facets_in_complex_to_off",[](Mesh_complex_3_in_triangulation_3_EPICK &c3, std::string fileName) {
      std::ofstream ofstr(fileName.c_str());
      c3.output_facets_in_complex_to_off(ofstr);
      ofstr.close();
    });

  // TODO understand why this does not work (does it not work with exact kernels?)
  //m.def("make_mesh_3",[](Polyhedral_mesh_domain_3_EPECK &d, Mesh_criteria_EPECK &c) {return CGAL::make_mesh_3<C3t3_EPECK>(d, c, CGAL::parameters::no_perturb(), CGAL::parameters::no_exclude());});
  m.def("make_mesh_3",[](Polyhedral_mesh_domain_3_EPICK &d, Mesh_criteria_3_EPICK &c) {return CGAL::make_mesh_3<Mesh_complex_3_in_triangulation_3_EPICK>(d, c, CGAL::parameters::no_perturb(), CGAL::parameters::no_exude());});

}