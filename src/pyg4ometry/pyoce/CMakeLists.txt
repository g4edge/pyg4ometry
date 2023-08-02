set(_sources
    BRep.cxx
    BRepBuilder.cxx
    BRepPrimAPI.cxx
    BRepMesh.cxx
    Geom.cxx
    gp.cxx
    Message.cxx
    Poly.cxx
    Standard.cxx
    STEPCAFControl.cxx
    StlAPI.cxx
    TCollection.cxx
    TDataStd.cxx
    TDF.cxx
    TDocStd.cxx
    TKernel.cxx
    TNaming.cxx
    TopAbs.cxx
    TopExp.cxx
    TopLoc.cxx
    TopoDS.cxx
    XCAFApp.cxx
    XCAFDoc.cxx)

if(${OpenCASCADE_VERSION} VERSION_LESS 7.7)
  message(STATUS "using patched OpenCASCADE headers")
endif()

foreach(_source ${_sources})
  configure_pybind11_extension(${_source} PACKAGE pyoce OUT_TARGET X)
  target_link_libraries(${X} PRIVATE ${OpenCASCADE_DataExchange_LIBRARIES})

  if(${OpenCASCADE_VERSION} VERSION_LESS 7.7)
    target_include_directories(${X} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/patches")
  endif()

  target_include_directories(${X} PRIVATE "${OpenCASCADE_INCLUDE_DIR}")
endforeach()
