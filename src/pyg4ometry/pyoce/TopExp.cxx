#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TopExp_Explorer.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TopExp, m) {
  py::class_<TopExp_Explorer> (m,"TopExp_Explorer")
    .def(py::init<>())
    .def(py::init<const TopoDS_Shape &, const TopAbs_ShapeEnum, const TopAbs_ShapeEnum>())
    .def("Init",&TopExp_Explorer::Init)
    .def("More",&TopExp_Explorer::More)
    .def("Next",&TopExp_Explorer::Next)
    .def("Value",&TopExp_Explorer::Value)
    .def("Current",&TopExp_Explorer::Current)
    .def("ReInit",&TopExp_Explorer::ReInit)
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("ExploredShape",&TopExp_Explorer::ExploredShape)
#endif
    .def("Depth",&TopExp_Explorer::Depth)
    .def("Clear",&TopExp_Explorer::Clear);
}