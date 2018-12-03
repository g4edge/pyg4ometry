cmake_minimum_required (VERSION 2.6)
project (ocReader)

# c++ 11
# add_definitions(-std=c++11)
add_definitions(-std=c++11 -stdlib=libc++  -fexceptions -fPIC -Wall -Wextra)

include(/Users/sboogert/Physics/codelocal/opencascade/opencascade-7.3.0_install/lib/cmake/opencascade/OpenCASCADEConfig.cmake)
message(STATUS "OpenCASCADE_INCLUDE_DIR ${OpenCASCADE_INCLUDE_DIR}")
message(STATUS "OpenCASCADE_LIBRARY_DIR ${OpenCASCADE_LIBRARY_DIR}")
message(STATUS "OpenCASCADE_LIBRARIES ${OpenCASCADE_LIBRARIES}")
link_directories(${OpenCASCADE_LIBRARY_DIR})

set (OpenCASCADE_LIBRARIES TKernel;TKMath;TKG2d;TKG3d;TKGeomBase;TKBRep;TKGeomAlgo;TKTopAlgo;TKPrim;TKBO;TKShHealing;TKBool;TKHLR;TKFillet;TKOffset;TKFeat;TKMesh;TKXMesh;TKService;TKV3d;TKOpenGl;TKMeshVS;TKCDF;TKLCAF;TKCAF;TKBinL;TKXmlL;TKBin;TKXml;TKStdL;TKStd;TKTObj;TKBinTObj;TKXmlTObj;TKVCAF;TKXSBase;TKSTEPBase;TKSTEPAttr;TKSTEP209;TKSTEP;TKIGES;TKXCAF;TKXDEIGES;TKXDESTEP;TKSTL;TKVRML;TKXmlXCAF;TKBinXCAF)

add_executable(test1 test1.cc)
target_include_directories(test1 PRIVATE ${OpenCASCADE_INCLUDE_DIR})
target_link_libraries(test1 ${OpenCASCADE_LIBRARIES})

add_executable(test2 test2.cc)
target_include_directories(test2 PRIVATE ${OpenCASCADE_INCLUDE_DIR})
target_link_libraries(test2 ${OpenCASCADE_LIBRARIES})

add_executable(test3 test3.cc)
# target_include_directories(test3 PRIVATE ${OpenCASCADE_INCLUDE_DIR})
target_link_libraries(test3 ${OpenCASCADE_LIBRARIES})

install(TARGETS test1 test2 DESTINATION bin)
