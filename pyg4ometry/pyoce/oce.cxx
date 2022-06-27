#include "oce.h"

StepFile::StepFile() {}

StepFile::~StepFile() {}


/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(oce, m) {
  py::class_<StepFile>(m,"StepFile")
    .def(py::init<>());
}
