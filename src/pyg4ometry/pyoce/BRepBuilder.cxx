#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <BRepBuilderAPI_Command.hxx>
#include <BRepBuilderAPI_MakeShape.hxx>
#include <BRepPrimAPI_MakeOneAxis.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPreviewAPI_MakeBox.hxx>
#include <BRepBuilderAPI_MakeShapeOnMesh.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(BRepBuilder, m) {
  py::class_<BRepBuilderAPI_Command>(m, "BRepBuilderAPI_Command")
    .def("IsDone",&BRepBuilderAPI_Command::IsDone)
    .def("Check",&BRepBuilderAPI_Command::Check);

  py::class_<BRepBuilderAPI_MakeShape, BRepBuilderAPI_Command>(m, "BRepBuilderAPI_MakeShape")
    .def("Build",[](BRepBuilderAPI_MakeShape &brb) { return brb.Build();})
    .def("Build",&BRepBuilderAPI_MakeShape::Build)
    .def("Shape",&BRepBuilderAPI_MakeShape::Shape)
    //.def("TopoDS_Shape",&BRepBuilderAPI_MakeShape::TopoDS_Shape) // TODO
    .def("Generated",&BRepBuilderAPI_MakeShape::Generated)
    .def("Modified",&BRepBuilderAPI_MakeShape::Modified)
    .def("IsDeleted",&BRepBuilderAPI_MakeShape::IsDeleted);

  py::class_<BRepPrimAPI_MakeBox, BRepBuilderAPI_MakeShape>(m,"BRepPrimAPI_MakeBox")
    .def(py::init<>())
    .def(py::init<const Standard_Real, const Standard_Real, const Standard_Real>())
    .def(py::init<const gp_Pnt &, const Standard_Real, const Standard_Real, const Standard_Real>())
    .def(py::init<const gp_Pnt &, const gp_Pnt &>());
    //.def(py::init<const gp_Ax2 &, const Standard_Real, const Standard_Real, const Standard_Real>); // TODO

  py::class_<BRepBuilderAPI_MakeShapeOnMesh, BRepBuilderAPI_MakeShape>(m,"BRepBuilderAPI_MakeShapeOnMesh")
    .def(py::init<const opencascade::handle<Poly_Triangulation>>());
}
