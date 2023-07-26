#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <BRepBuilderAPI_Command.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeShape.hxx>
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR > 6
#include <BRepBuilderAPI_MakeShapeOnMesh.hxx>
#endif
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_Sewing.hxx>
#include <TopoDS_Wire.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(BRepBuilder, m) {
  py::class_<BRepBuilderAPI_Command>(m, "BRepBuilderAPI_Command")
      .def("IsDone", &BRepBuilderAPI_Command::IsDone)
      .def("Check", &BRepBuilderAPI_Command::Check);

  py::class_<BRepBuilderAPI_MakeShape, BRepBuilderAPI_Command>(
      m, "BRepBuilderAPI_MakeShape")
      .def("Build", [](BRepBuilderAPI_MakeShape &brb) { return brb.Build(); })
      .def("Build", &BRepBuilderAPI_MakeShape::Build)
      .def("Shape", &BRepBuilderAPI_MakeShape::Shape)
      //.def("TopoDS_Shape",&BRepBuilderAPI_MakeShape::TopoDS_Shape) // TODO
      .def("Generated", &BRepBuilderAPI_MakeShape::Generated)
      .def("Modified", &BRepBuilderAPI_MakeShape::Modified)
      .def("IsDeleted", &BRepBuilderAPI_MakeShape::IsDeleted);

  py::class_<BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakeVertex")
      .def(py::init<const gp_Pnt &>())
      .def("Vertex", &BRepBuilderAPI_MakeVertex::Vertex);

  py::class_<BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakeEdge")
      .def(py::init<>());

  py::class_<BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakeWire")
      .def(py::init<>());

  py::class_<BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakePolygon")
      .def(py::init<const gp_Pnt &, const gp_Pnt &>())
      .def(py::init<const gp_Pnt &, const gp_Pnt &, const gp_Pnt &,
                    const Standard_Boolean>())
      .def(py::init<const gp_Pnt &, const gp_Pnt &, const gp_Pnt &,
                    const gp_Pnt &, const Standard_Boolean>())
      .def(py::init<const TopoDS_Vertex &, const TopoDS_Vertex &>())
      .def(py::init<const TopoDS_Vertex &, const TopoDS_Vertex &,
                    const TopoDS_Vertex &, const Standard_Boolean>())
      .def(py::init<const TopoDS_Vertex &, const TopoDS_Vertex &,
                    const TopoDS_Vertex &, const TopoDS_Vertex &,
                    const Standard_Boolean>())
      .def("Wire", &BRepBuilderAPI_MakePolygon::Wire);

  py::class_<BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakeFace")
      .def(py::init<>())
      .def(py::init<const TopoDS_Wire &,
                    const Standard_Boolean /*OnlyPlane*/>());

#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR > 6
  py::class_<BRepBuilderAPI_MakeShapeOnMesh, BRepBuilderAPI_MakeShape>(
      m, "BRepBuilderAPI_MakeShapeOnMesh")
      .def(py::init<const opencascade::handle<Poly_Triangulation>>());
#endif

  py::class_<BRepBuilderAPI_Sewing>(m, "BRepBuilderAPI_Sewing")
      .def(py::init<const Standard_Real /*tolerance=1.0e-06*/,
                    const Standard_Boolean /*option1=Standard_True*/,
                    const Standard_Boolean /*option2=Standard_True*/,
                    const Standard_Boolean /*option3=Standard_True*/,
                    const Standard_Boolean /*option4=Standard_False*/>())
      .def("Add", &BRepBuilderAPI_Sewing::Add)
      .def("Perform", &BRepBuilderAPI_Sewing::Perform)
      .def("SewedShape", &BRepBuilderAPI_Sewing::SewedShape);
}
