#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TDocStd_Document.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TDocStd, m) {
  py::class_<TDocStd_Document, opencascade::handle<TDocStd_Document>> (m,"TDocStd_Document")
    .def("Main",&TDocStd_Document::Main);
}