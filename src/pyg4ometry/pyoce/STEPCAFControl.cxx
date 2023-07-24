#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <Message_ProgressRange.hxx>
#include <STEPCAFControl_Reader.hxx>
#include <STEPCAFControl_Writer.hxx>
#include <TDocStd_Document.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(STEPCAFControl, m) {
  py::class_<STEPCAFControl_Reader>(m, "STEPCAFControl_Reader")
      .def(py::init<>())
      .def("SetColorMode", &STEPCAFControl_Reader::SetColorMode)
      .def("SetNameMode", &STEPCAFControl_Reader::SetNameMode)
      .def("SetLayerMode", &STEPCAFControl_Reader::SetLayerMode)
      .def("ReadFile",
           [](STEPCAFControl_Reader &reader,
              const Standard_CString filename) { // TODO-IFSelect_ReturnStatus
             reader.ReadFile(filename);
           })
      .def("Transfer", [](STEPCAFControl_Reader &reader,
                          opencascade::handle<TDocStd_Document> &doc,
                          const Message_ProgressRange &theProgress =
                              Message_ProgressRange()) {
        reader.Transfer(doc, theProgress);
      });

  py::class_<STEPCAFControl_Writer>(m, "STEPCAFControl_Writer")
      .def(py::init<>())
      .def("Transfer",
           [](STEPCAFControl_Writer &writer,
              opencascade::handle<TDocStd_Document> &doc) {
             writer.Transfer(doc);
           })
      .def("WriteFile",
           [](STEPCAFControl_Writer &writer, const Standard_CString filename) {
             writer.Write(filename);
           });
}
