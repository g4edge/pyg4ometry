pyoceExtensionMods = {'geom':['geom.cxx'],
		      'algo':['algo.cxx'],
		      'core':['core.cxx']}

foreach mod, srcs : pyoceExtensionMods
	py3.extension_module(mod,srcs,
			     dependencies : [pybind11, gmp, mpfr,cgal,boost],
			     cpp_args : ['-fvisibility=hidden','-std=c++14'])
endforeach

py3.extension_module('cgal','pyg4_cgal.cpp',
                      dependencies : [pybind11, gmp, mpfr, cgal,boost],
                      cpp_args : ['-std=c++14'])
