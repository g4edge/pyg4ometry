#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <XCAFDoc.hxx>
#include <XCAFDoc_ShapeTool.hxx>
#include <XCAFDoc_Location.hxx>
#include <XCAFDoc_ShapeMapTool.hxx>

#include <TopAbs.hxx>
#include <TopAbs_Orientation.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TopAbs, m) {
  py::enum_<TopAbs_ShapeEnum>(m,"TopAbs_ShapeEnum")
    .value("TopAbs_COMPOUND", TopAbs_ShapeEnum::TopAbs_COMPOUND)
    .value("TopAbs_COMPSOLID", TopAbs_ShapeEnum::TopAbs_COMPSOLID)
    .value("TopAbs_SOLID", TopAbs_ShapeEnum::TopAbs_SOLID)
    .value("TopAbs_SHELL", TopAbs_ShapeEnum::TopAbs_SHELL)
    .value("TopAbs_FACE", TopAbs_ShapeEnum::TopAbs_FACE)
    .value("TopAbs_WIRE", TopAbs_ShapeEnum::TopAbs_WIRE)
    .value("TopAbs_EDGE", TopAbs_ShapeEnum::TopAbs_EDGE)
    .value("TopAbs_VERTEX", TopAbs_ShapeEnum::TopAbs_VERTEX)
    .value("TopAbs_SHAPE", TopAbs_ShapeEnum::TopAbs_SHAPE)
    .export_values();

  py::enum_<TopAbs_Orientation>(m,"TopAbs_Orientation")
    .value("TopAbs_FORWARD", TopAbs_Orientation::TopAbs_FORWARD)
    .value("TopAbs_REVERSED", TopAbs_Orientation::TopAbs_REVERSED)
    .value("TopAbs_INTERNAL", TopAbs_Orientation::TopAbs_INTERNAL)
    .value("TopAbs_EXTERNAL", TopAbs_Orientation::TopAbs_EXTERNAL)
    .export_values();
}