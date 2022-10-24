#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel   Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                 Point_3_EPICK;
typedef Kernel_EPICK::Vector_3                                Vector_3_EPICK;
typedef CGAL::Surface_mesh<Kernel_EPICK::Point_3>             Surface_mesh_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel     Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                 Point_3_EPECK;
typedef Kernel_EPECK::Vector_3                                Vector_3_EPECK;
typedef CGAL::Surface_mesh<Kernel_EPECK::Point_3>             Surface_mesh_EPECK;

#include <CGAL/Aff_transformation_3.h>

typedef CGAL::Aff_transformation_3<Kernel_EPICK>              Aff_transformation_3_EPICK;
typedef CGAL::Aff_transformation_3<Kernel_EPECK>              Aff_transformation_3_EPECK;

#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/transform.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/distance.h>

PYBIND11_MODULE(Polygon_mesh_processing, m) {
   m.doc() = "CGAL Polygon mesh processing";
   m.def("reverse_face_orientations",[](Surface_mesh_EPICK &pm){ CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);},"Reverse all face orientations", py::arg("Surface_mesh"));
   m.def("triangulate_faces",[](Surface_mesh_EPICK &pm) {CGAL::Polygon_mesh_processing::triangulate_faces(pm);});
   m.def("transform",[](Aff_transformation_3_EPICK &transl, Surface_mesh_EPICK &sm){CGAL::Polygon_mesh_processing::transform(transl,sm);});
   m.def("corefine_and_compute_union",[](Surface_mesh_EPICK &pm1, Surface_mesh_EPICK &pm2, Surface_mesh_EPICK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1,pm2,out);});
   m.def("corefine_and_compute_intersection",[](Surface_mesh_EPICK &pm1, Surface_mesh_EPICK &pm2, Surface_mesh_EPICK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(pm1,pm2,out);});
   m.def("corefine_and_compute_difference",[](Surface_mesh_EPICK &pm1, Surface_mesh_EPICK &pm2, Surface_mesh_EPICK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_difference(pm1,pm2,out);});
   m.def("do_intersect",[](Surface_mesh_EPICK &pm1, Surface_mesh_EPICK &pm2){return CGAL::Polygon_mesh_processing::do_intersect(pm1,pm2);});
   m.def("area",[](Surface_mesh_EPICK &pm1) {return CGAL::to_double(CGAL::Polygon_mesh_processing::area(pm1));});
   m.def("volume",[](Surface_mesh_EPICK &pm1) {return CGAL::to_double(CGAL::Polygon_mesh_processing::volume(pm1));});

   m.def("reverse_face_orientations",[](Surface_mesh_EPECK &pm){ CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);},"Reverse all face orientations", py::arg("Surface_mesh"));
   m.def("triangulate_faces",[](Surface_mesh_EPECK &pm) {CGAL::Polygon_mesh_processing::triangulate_faces(pm);});
   m.def("transform",[](Aff_transformation_3_EPECK &transl, Surface_mesh_EPECK &sm){CGAL::Polygon_mesh_processing::transform(transl,sm);});
   m.def("corefine_and_compute_union",[](Surface_mesh_EPECK &pm1, Surface_mesh_EPECK &pm2, Surface_mesh_EPECK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1,pm2,out);});
   m.def("corefine_and_compute_intersection",[](Surface_mesh_EPECK &pm1, Surface_mesh_EPECK &pm2, Surface_mesh_EPECK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(pm1,pm2,out);});
   m.def("corefine_and_compute_difference",[](Surface_mesh_EPECK &pm1, Surface_mesh_EPECK &pm2, Surface_mesh_EPECK &out) {CGAL::Polygon_mesh_processing::corefine_and_compute_difference(pm1,pm2,out);});
   m.def("do_intersect",[](Surface_mesh_EPECK &pm1, Surface_mesh_EPECK &pm2){return CGAL::Polygon_mesh_processing::do_intersect(pm1,pm2);});
   m.def("area",[](Surface_mesh_EPECK &pm1) {return CGAL::to_double(CGAL::Polygon_mesh_processing::area(pm1));});
   m.def("volume",[](Surface_mesh_EPECK &pm1) {return CGAL::to_double(CGAL::Polygon_mesh_processing::volume(pm1));});

}