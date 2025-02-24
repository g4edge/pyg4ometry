#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <TopoDS.hxx>
#include <TopoDS_Builder.hxx>
#include <TopoDS_CompSolid.hxx>
#include <TopoDS_Compound.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Shell.hxx>
#include <TopoDS_Solid.hxx>
#include <TopoDS_TCompSolid.hxx>
#include <TopoDS_TCompound.hxx>
#include <TopoDS_TEdge.hxx>
#include <TopoDS_TFace.hxx>
#include <TopoDS_TShape.hxx>
#include <TopoDS_TVertex.hxx>
#include <TopoDS_TWire.hxx>
#include <TopoDS_Vertex.hxx>
#include <TopoDS_Wire.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TopoDS, m) {

#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR <= 8
  py::class_<TopoDS>(m, "TopoDSClass")
      .def_static("CompSolid",
                  [](TopoDS_Shape &shape) { return TopoDS::CompSolid(shape); })
      .def_static("Compound",
                  [](TopoDS_Shape &shape) { return TopoDS::Compound(shape); })
      .def_static("Edge",
                  [](TopoDS_Shape &shape) { return TopoDS::Edge(shape); })
      .def_static("Face",
                  [](TopoDS_Shape &shape) { return TopoDS::Face(shape); })
      .def_static("Shell",
                  [](TopoDS_Shape &shape) { return TopoDS::Shell(shape); })
      .def_static("Solid",
                  [](TopoDS_Shape &shape) { return TopoDS::Solid(shape); })
      .def_static("Wire",
                  [](TopoDS_Shape &shape) { return TopoDS::Wire(shape); })
      .def_static("Vertex",
                  [](TopoDS_Shape &shape) { return TopoDS::Vertex(shape); });
#else
  auto m_ns = m.def_submodule("TopoDSClass", "TopoDS namespace");
  m_ns.def("CompSolid",
           [](TopoDS_Shape &shape) { return TopoDS::CompSolid(shape); });
  m_ns.def("Compound",
           [](TopoDS_Shape &shape) { return TopoDS::Compound(shape); });
  m_ns.def("Edge", [](TopoDS_Shape &shape) { return TopoDS::Edge(shape); });
  m_ns.def("Face", [](TopoDS_Shape &shape) { return TopoDS::Face(shape); });
  m_ns.def("Shell", [](TopoDS_Shape &shape) { return TopoDS::Shell(shape); });
  m_ns.def("Solid", [](TopoDS_Shape &shape) { return TopoDS::Solid(shape); });
  m_ns.def("Wire", [](TopoDS_Shape &shape) { return TopoDS::Wire(shape); });
  m_ns.def("Vertex", [](TopoDS_Shape &shape) { return TopoDS::Vertex(shape); });
#endif
  py::class_<TopoDS_Builder>(m, "TopoDS_Builder")
      .def(py::init<>())
      .def("MakeWire", &TopoDS_Builder::MakeWire)
      .def("MakeShell", &TopoDS_Builder::MakeShell)
      .def("MakeSolid", &TopoDS_Builder::MakeSolid)
      .def("MakeCompSolid", &TopoDS_Builder::MakeCompSolid)
      .def("MakeCompound", &TopoDS_Builder::MakeCompound)
      .def("Add", &TopoDS_Builder::Add)
      .def("Remove", &TopoDS_Builder::Remove);

  py::class_<TopoDS_Shape>(m, "TopoDS_Shape")
      .def(py::init<>(), "TopoDS_Shape")
      .def("IsNull", &TopoDS_Shape::IsNull)
      .def("Nullify", &TopoDS_Shape::Nullify)
      .def("Location", [](TopoDS_Shape &shape) { return shape.Location(); })
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
      .def("Location",
           [](TopoDS_Shape &shape, const TopLoc_Location &loc,
              const Standard_Boolean theRaiseExc) {
             return shape.Location(loc, theRaiseExc);
           })
#else
  .def("Location", [](TopoDS_Shape &shape,const TopLoc_Location &loc) {return shape.Location(loc);})
#endif
      .def("Located", &TopoDS_Shape::Located)
      .def("Orientation",
           [](TopoDS_Shape &shape) { return shape.Orientation(); })
      .def("TShape", [](TopoDS_Shape &ts) { return ts.TShape(); })
      .def("ShapeType", &TopoDS_Shape::ShapeType)
      .def("NbChildren", &TopoDS_Shape::NbChildren)
      .def("DumpJson",
           [](TopoDS_Shape &shape) {
             py::scoped_ostream_redirect output;
             shape.DumpJson(std::cout);
           })
      .def("TopoDS_Face", [](TopoDS_Shape &shape) {
        return reinterpret_cast<TopoDS_Face &>(shape);
      });

  py::class_<TopoDS_CompSolid, TopoDS_Shape>(m, "TopoDS_CompSolid")
      .def(py::init<>());

  py::class_<TopoDS_Compound, TopoDS_Shape>(m, "TopoDS_Compound")
      .def(py::init<>());

  py::class_<TopoDS_Edge, TopoDS_Shape>(m, "TopoDS_Edge").def(py::init<>());

  py::class_<TopoDS_Face, TopoDS_Shape>(m, "TopoDS_Face").def(py::init<>());

  py::class_<TopoDS_Wire, TopoDS_Shape>(m, "TopoDS_Wire").def(py::init<>());

  py::class_<TopoDS_TShape>(m, "TopoDS_TShape");
  py::class_<TopoDS_TCompSolid, TopoDS_TShape>(m, "TopoDS_TCompSolid");
  py::class_<TopoDS_TCompound, TopoDS_TShape>(m, "TopoDS_TCompound");
  py::class_<TopoDS_TEdge, TopoDS_TShape>(m, "TopoDS_TEdge");
  py::class_<TopoDS_TFace, TopoDS_TShape>(m, "TopoDS_TFace");
  py::class_<TopoDS_TShell, TopoDS_TShape>(m, "TopoDS_TShell");
  py::class_<TopoDS_TVertex, TopoDS_TShape>(m, "TopoDS_TVertex");
  py::class_<TopoDS_TWire, TopoDS_TShape>(m, "TopoDS_TWire");
}
