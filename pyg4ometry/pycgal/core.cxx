#include <pybind11/pybind11.h>

class CSG {
protected : 
  int _polygonCount =0;

public:
  CSG() {};
  ~CSG() {};
  
  int polygonCount() {return _polygonCount;};

};

namespace py = pybind11;

PYBIND11_MODULE(core, m) {
  py::class_<CSG>(m,"CSG")
    .def(py::init<>())
    .def("polygonCount", &CSG::polygonCount);
}
