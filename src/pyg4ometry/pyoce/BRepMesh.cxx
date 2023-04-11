#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <BRepMesh_IncrementalMesh.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(BRepMesh, m) {
  py::class_<BRepMesh_IncrementalMesh, opencascade::handle<BRepMesh_IncrementalMesh>> (m,"BRepMesh_IncrementalMesh")
    .def(py::init<>())
    .def(py::init<const TopoDS_Shape &,
                  const Standard_Real,
                  const Standard_Boolean,
                  const Standard_Real,
                  const Standard_Boolean>())
    .def(py::init<const TopoDS_Shape &,
                  const IMeshTools_Parameters,
                  const Message_ProgressRange>());
}