#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <STEPCAFControl_Reader.hxx>
#include <TDocStd_Document.hxx>
#include <Message_ProgressRange.hxx>
/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(STEPCAFControl, m) {
  py::class_<STEPCAFControl_Reader>(m,"STEPCAFControl_Reader")
    .def(py::init<>())
    .def("SetColorMode",&STEPCAFControl_Reader::SetColorMode)
    .def("SetNameMode",&STEPCAFControl_Reader::SetNameMode)
    .def("SetLayerMode",&STEPCAFControl_Reader::SetLayerMode)
    .def("ReadFile",[](STEPCAFControl_Reader &reader, const Standard_CString filename) { // TODO-IFSelect_ReturnStatus
                         reader.ReadFile(filename);
                       })
    .def("Transfer",[](STEPCAFControl_Reader &reader,
                       opencascade::handle<TDocStd_Document> &doc,
                       const Message_ProgressRange &theProgress=Message_ProgressRange()){
                         reader.Transfer(doc,theProgress);
                       });
}