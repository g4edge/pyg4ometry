cmake_minimum_required(VERSION 3.20 FATAL_ERROR)

project(pyg4ometry)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake/modules/)

# set version dynamically with https://github.com/LecrisUT/CMakeExtraUtils
# FIXME: breaks on GitHub Actions runners
# cmake_policy(SET CMP0140 NEW)
# include(DynamicVersion)
# dynamic_version(PROJECT_PREFIX pyg4ometry_)
# project(pyg4ometry VERSION ${PROJECT_VERSION})

# Set a default build type if none was specified
# FIXME when first stable version is out
set(default_build_type "Release")

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE
      "${default_build_type}"
      CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE
      PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
else()
  message(STATUS "Setting build type to '${CMAKE_BUILD_TYPE}'")
endif()

# see pyproject.toml for version bounds
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

# TODO: meaningful version bounds
find_package(CGAL 5.0 REQUIRED)
message(STATUS "Found CGAL (found version \"${CGAL_VERSION}\")")
find_package(Boost REQUIRED)
find_package(OpenCASCADE)
find_package(OpenCASCADE
  COMPONENTS FoundationClasses ModelingAlgorithms
             ModelingData DataExchange Visualization
  REQUIRED)

# somehow the OpenCASCADE CMake files do no support version
# inequality comparisons. workaround:
set(OPENCASCADE_MIN_VERSION 7.5)
if(${OpenCASCADE_VERSION} VERSION_GREATER_EQUAL ${OPENCASCADE_MIN_VERSION})
  message(STATUS "Found OpenCASCADE (found version \"${OpenCASCADE_VERSION}\")")
else()
  message(FATAL_ERROR
    "Could not find suitable OpenCASCADE version"
    "(required ${OPENCASCADE_MIN_VERSION}, ${OpenCASCADE_VERSION} found)")
endif()

add_subdirectory(src/pyg4ometry)
