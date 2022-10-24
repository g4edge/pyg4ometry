#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Standard_GUID.hxx>
#include <TNaming_NamedShape.hxx>
#include <TopoDS_Shape.hxx>
/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TNaming, m) {
  py::class_<TNaming_NamedShape, opencascade::handle<TNaming_NamedShape>, TDF_Attribute>(m,"TNaming_NamedShape")
    .def(py::init([](){return opencascade::handle<TNaming_NamedShape>(new TNaming_NamedShape());}))
    .def("ID", &TNaming_NamedShape::ID)
    .def("Dump",[](TNaming_NamedShape &name) { py::scoped_ostream_redirect output; name.Dump(std::cout);})
    .def("Get",&TNaming_NamedShape::Get)
    .def_static("GetID",&TNaming_NamedShape::GetID);
}