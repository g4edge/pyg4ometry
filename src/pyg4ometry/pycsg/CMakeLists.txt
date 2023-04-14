include(SkbuildUtils)

set(_sources
    core.pyx
    geom.pyx)

foreach(_source ${_sources})
  configure_cython_extension(${_source} PACKAGE pycsg)
endforeach()
