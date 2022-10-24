cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(pyg4ometry)

# Set a default build type if none was specified
# CHANGEME when first stable version is out
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

add_subdirectory(src/pyg4ometry/pycgal)
add_subdirectory(src/pyg4ometry/pyoce)
