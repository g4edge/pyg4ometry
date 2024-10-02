#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

// #define CGAL_PMP_USE_CERES_SOLVER

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_rational.h>
#include <CGAL/Extended_cartesian.h>
#include <CGAL/Surface_mesh.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Point_3 Point_3_EPICK;
typedef Kernel_EPICK::Vector_3 Vector_3_EPICK;
typedef CGAL::Surface_mesh<Kernel_EPICK::Point_3> Surface_mesh_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Point_3 Point_3_EPECK;
typedef Kernel_EPECK::Vector_3 Vector_3_EPECK;
typedef CGAL::Surface_mesh<Kernel_EPECK::Point_3> Surface_mesh_EPECK;

typedef CGAL::Extended_cartesian<CGAL::Exact_rational> Kernel_ECER;
typedef Kernel_ECER::Point_3 Point_3_ECER;
typedef Kernel_ECER::Vector_3 Vector_3_ECER;
typedef CGAL::Surface_mesh<Kernel_ECER::Point_3> Surface_mesh_ECER;

#include <CGAL/Aff_transformation_3.h>

typedef CGAL::Aff_transformation_3<Kernel_EPICK> Aff_transformation_3_EPICK;
typedef CGAL::Aff_transformation_3<Kernel_EPECK> Aff_transformation_3_EPECK;
typedef CGAL::Aff_transformation_3<Kernel_ECER> Aff_transformation_3_ECER;

#include <CGAL/Polygon_mesh_processing/border.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/distance.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>
// #include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/transform.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
// #include <CGAL/Polygon_mesh_processing/angle_and_area_smoothing.h>
// #include <CGAL/Polygon_mesh_processing/smooth_mesh.h>
#include <CGAL/Polygon_mesh_processing/smooth_shape.h>

PYBIND11_MODULE(Polygon_mesh_processing, m) {

  /**********************************************************************
  EPICK
  **********************************************************************/

  m.doc() = "CGAL Polygon mesh processing";
  m.def(
      "reverse_face_orientations",
      [](Surface_mesh_EPICK &pm) {
        CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);
      },
      "Reverse all face orientations", py::arg("Surface_mesh"));
  m.def("triangulate_faces", [](Surface_mesh_EPICK &pm) {
    CGAL::Polygon_mesh_processing::triangulate_faces(pm);
  });
  m.def("transform",
        [](Aff_transformation_3_EPICK &transl, Surface_mesh_EPICK &sm) {
          CGAL::Polygon_mesh_processing::transform(transl, sm);
        });
  m.def("corefine_and_compute_union", [](Surface_mesh_EPICK &pm1,
                                         Surface_mesh_EPICK &pm2,
                                         Surface_mesh_EPICK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1, pm2, out);
  });
  m.def("corefine_and_compute_intersection", [](Surface_mesh_EPICK &pm1,
                                                Surface_mesh_EPICK &pm2,
                                                Surface_mesh_EPICK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(pm1, pm2,
                                                                     out);
  });
  m.def("corefine_and_compute_difference", [](Surface_mesh_EPICK &pm1,
                                              Surface_mesh_EPICK &pm2,
                                              Surface_mesh_EPICK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_difference(pm1, pm2,
                                                                   out);
  });
  m.def("does_self_intersect", [](Surface_mesh_EPICK &pm) {
    return CGAL::Polygon_mesh_processing::does_self_intersect(pm);
  });
  m.def("do_intersect", [](Surface_mesh_EPICK &pm1, Surface_mesh_EPICK &pm2) {
    return CGAL::Polygon_mesh_processing::do_intersect(pm1, pm2);
  });
  m.def("area", [](Surface_mesh_EPICK &pm1) {
    return CGAL::to_double(CGAL::Polygon_mesh_processing::area(pm1));
  });
  m.def("volume", [](Surface_mesh_EPICK &pm1) {
    return CGAL::to_double(CGAL::Polygon_mesh_processing::volume(pm1));
  });
  //  m.def("isotropic_remeshing", [](Surface_mesh_EPICK &pm1,
  //                                  double target_mesh_length, int nb_iter) {
  //    return CGAL::Polygon_mesh_processing::isotropic_remeshing(
  //        faces(pm1), target_mesh_length, pm1,
  //        CGAL::parameters::number_of_iterations(nb_iter).protect_constraints(
  //            true));
  //  });
  /*
  m.def("angle_and_area_smoothing", [](Surface_mesh_EPICK &pm1, int nb_iter) {
    return CGAL::Polygon_mesh_processing::angle_and_area_smoothing(pm1,
                                                                   CGAL::parameters::number_of_iterations(nb_iter)
                                                                     .use_safety_constraints(false));
  });
  m.def("tangential_relaxation", [](Surface_mesh_EPICK &pm1, int nb_iter) {
    return CGAL::Polygon_mesh_processing::tangential_relaxation(pm1,
                                                                CGAL::parameters::number_of_iterations(nb_iter));
  });
  m.def("smooth_shape", [](Surface_mesh_EPICK &pm1, double time, int nb_iter) {
    return CGAL::Polygon_mesh_processing::smooth_shape(face(pm1),
                                                       pm1,
                                                       time,
                                                       CGAL::parameters::number_of_iterations(nb_iter));
  });
  */

  /**********************************************************************
  EPECK
  **********************************************************************/

  m.def(
      "reverse_face_orientations",
      [](Surface_mesh_EPECK &pm) {
        CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);
      },
      "Reverse all face orientations", py::arg("Surface_mesh"));
  m.def("triangulate_faces", [](Surface_mesh_EPECK &pm) {
    CGAL::Polygon_mesh_processing::triangulate_faces(pm);
  });
  m.def("transform",
        [](Aff_transformation_3_EPECK &transl, Surface_mesh_EPECK &sm) {
          CGAL::Polygon_mesh_processing::transform(transl, sm);
        });
  m.def("corefine_and_compute_union", [](Surface_mesh_EPECK &pm1,
                                         Surface_mesh_EPECK &pm2,
                                         Surface_mesh_EPECK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1, pm2, out);
  });
  m.def("corefine_and_compute_intersection", [](Surface_mesh_EPECK &pm1,
                                                Surface_mesh_EPECK &pm2,
                                                Surface_mesh_EPECK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(pm1, pm2,
                                                                     out);
  });
  m.def("corefine_and_compute_difference", [](Surface_mesh_EPECK &pm1,
                                              Surface_mesh_EPECK &pm2,
                                              Surface_mesh_EPECK &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_difference(pm1, pm2,
                                                                   out);
  });
  m.def("does_self_intersect", [](Surface_mesh_EPECK &pm) {
    return CGAL::Polygon_mesh_processing::does_self_intersect(pm);
  });
  m.def("do_intersect", [](Surface_mesh_EPECK &pm1, Surface_mesh_EPECK &pm2) {
    return CGAL::Polygon_mesh_processing::do_intersect(pm1, pm2);
  });
  m.def("area", [](Surface_mesh_EPECK &pm1) {
    return CGAL::to_double(CGAL::Polygon_mesh_processing::area(pm1));
  });
  m.def("volume", [](Surface_mesh_EPECK &pm1) {
    return CGAL::to_double(CGAL::Polygon_mesh_processing::volume(pm1));
  });
  //  m.def("isotropic_remeshing", [](Surface_mesh_EPECK &pm1,
  //                                  double target_mesh_length, int nb_iter) {
  //    return CGAL::Polygon_mesh_processing::isotropic_remeshing(
  //        faces(pm1), target_mesh_length, pm1,
  //        CGAL::parameters::number_of_iterations(nb_iter).protect_constraints(
  //            true));
  //  });

  /**********************************************************************
  ECER
  **********************************************************************/
  /*
  m.def(
      "reverse_face_orientations",
      [](Surface_mesh_ECER &pm) {
        CGAL::Polygon_mesh_processing::reverse_face_orientations(pm);
      },
      "Reverse all face orientations", py::arg("Surface_mesh"));
  m.def("transform",
        [](Aff_transformation_3_ECER &transl, Surface_mesh_ECER &sm) {
          CGAL::Polygon_mesh_processing::transform(transl, sm);
        });
  m.def("corefine_and_compute_union", [](Surface_mesh_ECER &pm1,
                                         Surface_mesh_ECER &pm2,
                                         Surface_mesh_ECER &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_union(pm1, pm2, out);
  });

  m.def("corefine_and_compute_intersection", [](Surface_mesh_ECER &pm1,
                                                Surface_mesh_ECER &pm2,
                                                Surface_mesh_ECER &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(pm1, pm2,
                                                                     out);
  });
  m.def("corefine_and_compute_difference", [](Surface_mesh_ECER &pm1,
                                              Surface_mesh_ECER &pm2,
                                              Surface_mesh_ECER &out) {
    CGAL::Polygon_mesh_processing::corefine_and_compute_difference(pm1, pm2,
                                                                   out);
  });
  m.def("do_intersect", [](Surface_mesh_ECER &pm1, Surface_mesh_ECER &pm2) {
    return CGAL::Polygon_mesh_processing::do_intersect(pm1, pm2);
  });
  */
}
