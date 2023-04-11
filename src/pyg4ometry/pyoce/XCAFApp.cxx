#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <XCAFApp_Application.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(XCAFApp, m) {
  py::class_<XCAFApp_Application, opencascade::handle<XCAFApp_Application>>(m,"XCAFApp_Application")
    .def_static("GetApplication",XCAFApp_Application::GetApplication)
    .def("NewDocument",[](XCAFApp_Application &hApp, const TCollection_ExtendedString &format){
        opencascade::handle<TDocStd_Document> hDoc;
        hApp.NewDocument(format, hDoc);
        return hDoc;
    });
}