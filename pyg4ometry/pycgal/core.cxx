//
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` core.cxx -o core`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m
//

#include "core.h"

CSG::CSG() {}

CSG::~CSG() {}

CSG CSG::fromPolygons(py::list &polygons) {
  CSG csg;
  csg._polygons = polygons;
  return csg;
}

py::list CSG::polygons() {
  return _polygons;
}

PYBIND11_MODULE(core, m) {
  py::class_<CSG>(m,"CSG")
    .def(py::init<>())
    .def("fromPolygons",&CSG::fromPolygons)
    .def("polygons",&CSG::polygons)
    .def_readwrite("polygons",&CSG::_polygons);
}
