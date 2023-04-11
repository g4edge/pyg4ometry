#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Standard_Transient.hxx>
#include <Standard_GUID.hxx>
#include <Standard_Type.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TKernel, m) {

  py::class_<Standard_Transient, opencascade::handle<Standard_Transient>> (m,"Standard_Transient")
    .def("DynamicType",&Standard_Transient::DynamicType)
    .def_static("get_type_name", &Standard_Transient::get_type_name);

  py::class_<Standard_GUID> (m,"Standard_GUID");

  py::class_<Standard_Type, opencascade::handle<Standard_Type>, Standard_Transient>(m,"Standard_Type")
    .def("Name",&Standard_Type::Name)
    .def("SystemName",&Standard_Type::SystemName);
}