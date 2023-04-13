set(sources
    BRep.cxx
    BRepMesh.cxx
    Geom.cxx
    gp.cxx
    Message.cxx
    Poly.cxx
    STEPCAFControl.cxx
    StlAPI.cxx
    TCollection.cxx
    TDataStd.cxx
    TDF.cxx
    TDocStd.cxx
    # TKernel.cxx
    TNaming.cxx
    TopAbs.cxx
    TopExp.cxx
    TopLoc.cxx
    TopoDS.cxx
    XCAFApp.cxx
    XCAFDoc.cxx)

foreach(source ${sources})

  cmake_path(GET source STEM module)

  pybind11_add_module(${module} ${source})

  target_link_libraries(${module} PRIVATE ${OpenCASCADE_DataExchange_LIBRARIES})
  target_include_directories(${module} PRIVATE "${OpenCASCADE_INCLUDE_DIR}")

  install(TARGETS ${module} DESTINATION ${SKBUILD_PROJECT_NAME}/pyoce)

endforeach()
