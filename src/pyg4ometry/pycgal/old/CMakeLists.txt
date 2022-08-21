cmake_minimum_required(VERSION 3.16)


set(CMAKE_BUILD_TYPE Release)

set(CMAKE_VERBOSE_MAKEFILE ON)


project(pycgal
  VERSION 0.1
  DESCRIPTION "Wrapper for cgal with python bindings."
  LANGUAGES CXX
  )

include(CMakePrintHelpers)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(pybind11)
find_package(CGAL REQUIRED COMPONENTS Core)
find_package(Boost REQUIRED)
set(Boost_USE_MULTITHREADED ON)


pybind11_add_module(geom SHARED geom.cxx)
pybind11_add_module(algo SHARED algo.cxx)
pybind11_add_module(core SHARED core.cxx)

# ALGO
target_include_directories(algo PUBLIC "${CGAL_INCLUDE_DIRS}")
target_link_libraries(algo
  PRIVATE
  CGAL::CGAL_Core
  CGAL::CGAL
  geom
  )

# CORE
target_include_directories(core PUBLIC "${CGAL_INCLUDE_DIRS}")
target_link_libraries(core
  PRIVATE
  CGAL::CGAL_Core
  CGAL::CGAL
  geom
  algo
  )

# cmake_print_properties(TARGETS geom PROPERTIES LINK_LIBRARIES)
