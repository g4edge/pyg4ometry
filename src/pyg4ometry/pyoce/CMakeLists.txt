set(_sources
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
    TKernel.cxx
    TNaming.cxx
    TopAbs.cxx
    TopExp.cxx
    TopLoc.cxx
    TopoDS.cxx
    XCAFApp.cxx
    XCAFDoc.cxx)

foreach(_source ${_sources})
  configure_pybind11_extension(${_source} PACKAGE pyoce OUT_TARGET X)
  target_link_libraries(${X} PRIVATE ${OpenCASCADE_DataExchange_LIBRARIES})
  target_include_directories(${X} PRIVATE "${OpenCASCADE_INCLUDE_DIR}")
endforeach()
