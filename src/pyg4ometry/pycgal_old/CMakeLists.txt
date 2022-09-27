cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(pycgal)

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
find_package(CGAL REQUIRED)  # TODO: version?
find_package(Boost REQUIRED)

# Create the pybind11 library
add_library(${CMAKE_PROJECT_NAME} MODULE algo.cxx algo.h core.cxx core.h geom.cxx geom.h)

target_link_libraries(${CMAKE_PROJECT_NAME}
    PRIVATE
        pybind11::module
        pybind11::lto
        CGAL::CGAL)

target_include_directories(
  ${CMAKE_PROJECT_NAME}
    PUBLIC "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}")

pybind11_extension(${CMAKE_PROJECT_NAME})

if(NOT MSVC AND NOT ${CMAKE_BUILD_TYPE} MATCHES Debug|RelWithDebInfo)
  # Strip unnecessary sections of the binary on Linux/macOS
  pybind11_strip(${CMAKE_PROJECT_NAME})
endif()

set_target_properties(${CMAKE_PROJECT_NAME}
    PROPERTIES
        CXX_VISIBILITY_PRESET "hidden"
        CUDA_VISIBILITY_PRESET "hidden")

# PYG4OMETRY_VERSION_INFO is defined by setup.py and passed into the C++ code
# as a define (VERSION_INFO) here.
target_compile_definitions(${CMAKE_PROJECT_NAME}
    PRIVATE VERSION_INFO=${PYG4OMETRY_VERSION_INFO})

install(TARGETS ${CMAKE_PROJECT_NAME} DESTINATION .)
