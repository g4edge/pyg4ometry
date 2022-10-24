cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(pyoce)

if(SKBUILD)
  # Scikit-Build does not add your site-packages to the search path
  # automatically, so we need to add it _or_ the pybind11 specific directory
  # here.
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c
            "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE _tmp_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
  list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
endif()

find_package(pybind11 2.6 CONFIG REQUIRED)
find_package(OpenCASCADE)
find_package(OpenCASCADE COMPONENTS FoundationClasses REQUIRED)
find_package(OpenCASCADE COMPONENTS ModelingAlgorithms REQUIRED)
find_package(OpenCASCADE COMPONENTS ModelingData REQUIRED)
find_package(OpenCASCADE COMPONENTS DataExchange REQUIRED)
find_package(OpenCASCADE COMPONENTS Visualization REQUIRED)

# workaround: somehow the OpenCASCADE CMake files do no support version inequality comparisons
set(OPENCASCADE_MIN_VERSION 7.5)
if(${OpenCASCADE_VERSION} VERSION_GREATER_EQUAL ${OPENCASCADE_MIN_VERSION})
  message(STATUS "Found OpenCASCADE (found version \"${OpenCASCADE_VERSION}\")")
else()
  message(FATAL_ERROR
    "Could not find suitable OpenCASCADE version"
    "(required ${OPENCASCADE_MIN_VERSION}, ${OpenCASCADE_VERSION} found)")
endif()

# Create the pybind11 library
# https://pybind11.readthedocs.io/en/stable/compiling.html#building-with-cmake
# https://pybind11.readthedocs.io/en/stable/compiling.html#advanced-interface-library-targets

set(extnSources TCollection.cxx TKernel.cxx  TDocStd.cxx TDataStd.cxx
                TNaming.cxx TDF.cxx TopoDS.cxx gp.cxx Geom.cxx Poly.cxx
                XCAFDoc.cxx TopAbs.cxx TopLoc.cxx TopExp.cxx Message.cxx
                BRep.cxx BRepMesh.cxx StlAPI.cxx XCAFApp.cxx STEPCAFControl.cxx)

foreach(extnSource ${extnSources})
    string(REPLACE .cxx "" extnName ${extnSource})
    set(extnName temp_${extnName})
    message(STATUS "pybind extension " ${extnName} " " ${extnSource})
    add_library(${extnName} MODULE ${extnSource})

    target_link_libraries(${extnName}
        PRIVATE
        pybind11::module
        pybind11::lto
        ${OpenCASCADE_DataExchange_LIBRARIES})

    target_include_directories(${extnName}
        PUBLIC "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}"
        PRIVATE "${OpenCASCADE_INCLUDE_DIR}")

    pybind11_extension(${extnName})

    if(NOT MSVC AND NOT ${CMAKE_BUILD_TYPE} MATCHES Debug|RelWithDebInfo)
        # Strip unnecessary sections of the binary on Linux/macOS
        pybind11_strip(${extnName})
    endif()

    set_target_properties(${extnName}
        PROPERTIES
        CXX_VISIBILITY_PRESET "hidden"
        CUDA_VISIBILITY_PRESET "hidden")

    # PYG4OMETRY_VERSION_INFO is defined by setup.py and passed into the C++ code
    # as a define (VERSION_INFO) here.
    target_compile_definitions(${extnName}
        PRIVATE VERSION_INFO=${PYG4OMETRY_VERSION_INFO})

    install(TARGETS ${extnName} DESTINATION .)

endforeach()
