set(_sources
    core
    geom)

foreach(_source ${_sources})
  set(_target pycsg_${_source})
  add_cython_target(${_target} ${_source}.pyx OUTPUT_VAR X)
  add_library(${_target} MODULE ${X})
  python_extension_module(${_target})
  set_target_properties(${_target} PROPERTIES LIBRARY_OUTPUT_NAME ${_source})

  install(TARGETS ${_target} LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}/pycsg)
endforeach()
