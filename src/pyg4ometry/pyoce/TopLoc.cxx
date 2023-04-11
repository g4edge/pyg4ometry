#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TopLoc_Location.hxx>
#include <TopLoc_Datum3D.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TopLoc, m) {
  py::class_<TopLoc_Location>(m,"TopLoc_Location")
    .def(py::init<>())
    .def("FirstDatum",[](TopLoc_Location &location) {return location.FirstDatum();})
    .def("ShallowDump",[](TopLoc_Location &location) {py::scoped_ostream_redirect output; location.ShallowDump(std::cout);})
    .def("Transformation",[](TopLoc_Location &location) {return location.Transformation();});

  py::class_<TopLoc_Datum3D, opencascade::handle<TopLoc_Datum3D>, Standard_Transient>(m,"TopLoc_Datum3D")
    .def(py::init<>())
    .def("ShallowDump",[](TopLoc_Location &location) {py::scoped_ostream_redirect output; location.ShallowDump(std::cout);});

}