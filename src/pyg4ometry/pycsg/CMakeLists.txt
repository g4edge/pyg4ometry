find_package(skbuild)
find_package(PythonExtensions)
find_package(Cython)

project(pycsg)
# Note: In this case, either one of these arguments may be omitted; their
# value would have been inferred from that of the other.
add_cython_target(code core.pyx)
add_library(core MODULE core.pyx)
