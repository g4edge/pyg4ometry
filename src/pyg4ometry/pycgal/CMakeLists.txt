set(sources
    Aff_transformation_3.cxx
    Bbox_3.cxx
    # CGAL.cxx
    Circle_3.cxx
    Direction_3.cxx
    geom.cxx
    Iso_cuboid_3.cxx
    Line_3.cxx
    Nef_polyhedron_3.cxx
    Partition_traits_2_Polygon_2.cxx
    Plane_3.cxx
    Point_2.cxx
    Point_3.cxx
    Polygon_2.cxx
    Polygon_mesh_processing.cxx
    Polygon_with_holes_2.cxx
    Polyhedron_3.cxx
    Ray_3.cxx
    Segment_3.cxx
    Surface_mesh.cxx
    Triangle_2.cxx
    Triangle_3.cxx
    Vector_2.cxx
    Vector_3.cxx)

foreach(source ${sources})

  cmake_path(GET source STEM module)

  pybind11_add_module(${module} ${source})
  target_link_libraries(${module} PRIVATE CGAL::CGAL)

  install(TARGETS ${module} DESTINATION ${SKBUILD_PROJECT_NAME}/pycgal)

endforeach()
