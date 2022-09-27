pyx_core = custom_target(
  'core.c',
  output : 'core.c',
  input : 'core.pyx',
  command : [cython, '@INPUT@', '-o', '@OUTPUT@'],
)

pyx_geom = custom_target(
  'geom.c',
  output : 'geom.c',
  input : 'geom.pyx',
  command : [cython, '@INPUT@', '-o', '@OUTPUT@'],
)

py3.extension_module(
  'core',
  pyx_core,
  install : true
)

py3.extension_module(
  'geom',
  pyx_geom,
  install : true
)
