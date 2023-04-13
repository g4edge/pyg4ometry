add_cython_target(core)
add_library(core MODULE ${core})
python_extension_module(core)

add_cython_target(geom)
add_library(geom MODULE ${geom})
python_extension_module(geom)

install(TARGETS core geom LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}/pycsg)
install(FILES __init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/pycsg)
