# wraps add_cython_target to allow for scoping
function(configure_cython_extension _source)
  cmake_parse_arguments(_args "" "PACKAGE;OUT_TARGET" "" ${ARGN})

  cmake_path(GET _source STEM _module)

  # FIXME: cannot do arbitrary scoping of target, e.g.
  #
  #   set(_target ${_args_PACKAGE}_${_module})
  #
  # it generates these errors:
  #
  #   ImportError: dynamic module does not define module export function (PyInit_geom)
  #
  # This way, however, there is no way to disambiguate if another CMake target
  # with the same name exists
  set(_target ${_module})
  add_cython_target(${_target} ${_source} OUTPUT_VAR X)
  add_library(${_target} MODULE ${X})
  python_extension_module(${_target})
  set_target_properties(${_target} PROPERTIES LIBRARY_OUTPUT_NAME ${_module})
  install(TARGETS ${_target} LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}/${_args_PACKAGE})

  if (_args_OUT_TARGET)
    set(${_args_OUT_TARGET} ${_target} PARENT_SCOPE)
  endif()
endfunction()

# wraps pybind11_add_module() to allow for scoping
function(configure_pybind11_extension _source)
  cmake_parse_arguments(_args "" "PACKAGE;OUT_TARGET" "" ${ARGN})

  cmake_path(GET _source STEM _module)
  set(_target ${_args_PACKAGE}_${_module})
  pybind11_add_module(${_target} ${_source})
  set_target_properties(${_target} PROPERTIES LIBRARY_OUTPUT_NAME ${_module})
  install(TARGETS ${_target} DESTINATION ${SKBUILD_PROJECT_NAME}/${_args_PACKAGE})

  if (_args_OUT_TARGET)
    set(${_args_OUT_TARGET} ${_target} PARENT_SCOPE)
  endif()
endfunction()
