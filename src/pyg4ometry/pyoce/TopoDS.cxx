#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TopoDS.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_TShape.hxx>
#include <TopoDS_TFace.hxx>
#include <TopoDS_TEdge.hxx>
#include <TopoDS_TWire.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TopoDS, m) {
  py::class_<TopoDS>(m,"TopoDSClass")
    .def_static("Edge",[](TopoDS_Shape &shape) {return TopoDS::Edge(shape);})
    .def_static("Face",[](TopoDS_Shape &shape) {return TopoDS::Face(shape);})
    .def_static("Wire",[](TopoDS_Shape &shape) {return TopoDS::Wire(shape);});

  py::class_<TopoDS_Shape> (m,"TopoDS_Shape")
    .def(py::init<>())
    .def("IsNull",&TopoDS_Shape::IsNull)
    .def("NbChildren",&TopoDS_Shape::NbChildren)
    .def("Nullify", &TopoDS_Shape::Nullify)
    .def("Location", [](TopoDS_Shape &shape) {return shape.Location();})
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("Location", [](TopoDS_Shape &shape,const TopLoc_Location &loc, const Standard_Boolean theRaiseExc) {return shape.Location(loc,theRaiseExc);})
#else
    .def("Location", [](TopoDS_Shape &shape,const TopLoc_Location &loc) {return shape.Location(loc);})
#endif
    .def("Orientation",[](TopoDS_Shape &shape) {return shape.Orientation();})
    .def("ShapeType",&TopoDS_Shape::ShapeType)
    .def("DumpJson", [](TopoDS_Shape &shape) {py::scoped_ostream_redirect output; shape.DumpJson(std::cout);});

  py::class_<TopoDS_Face, TopoDS_Shape>(m,"TopoDS_Face")
    .def(py::init<>());

  py::class_<TopoDS_Wire, TopoDS_Shape>(m,"TopoDS_Wire")
    .def(py::init<>());

  py::class_<TopoDS_Edge, TopoDS_Shape>(m,"TopoDS_Edge")
    .def(py::init<>());

  py::class_<TopoDS_TShape>(m,"TopoDS_TShape");
  py::class_<TopoDS_TFace, TopoDS_TShape>(m,"TopoDS_TFace");
  py::class_<TopoDS_TWire, TopoDS_TShape>(m,"TopoDS_TWire");
}