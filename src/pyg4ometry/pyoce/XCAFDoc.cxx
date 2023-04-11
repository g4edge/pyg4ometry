#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <XCAFDoc.hxx>
#include <XCAFDoc_DocumentTool.hxx>
#include <XCAFDoc_ShapeTool.hxx>
#include <XCAFDoc_ColorTool.hxx>
#include <XCAFDoc_Location.hxx>
#include <XCAFDoc_ShapeMapTool.hxx>

#include <Standard_GUID.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(XCAFDoc, m) {

  py::class_<XCAFDoc>(m, "XCAFDocClass")
    .def_static("AssemblyGUID",&XCAFDoc::AssemblyGUID)
    .def_static("ShapeRefGUID",&XCAFDoc::ShapeRefGUID)
    .def_static("ColorRefGUID",&XCAFDoc::ColorRefGUID)
    .def_static("DimTolRefGUID",&XCAFDoc::DimTolRefGUID)
    .def_static("DimensionRefFirstGUID",&XCAFDoc::DimensionRefFirstGUID)
    .def_static("DimensionRefSecondGUID", &XCAFDoc::DimensionRefSecondGUID)
    .def_static("GeomToleranceRefGUID",&XCAFDoc::GeomToleranceRefGUID);

  py::class_<XCAFDoc_DocumentTool, opencascade::handle<XCAFDoc_DocumentTool>, TDF_Attribute>(m,"XCAFDoc_DocumentTool")
    .def_static("ShapeTool",&XCAFDoc_DocumentTool::ShapeTool)
    .def_static("ColorTool",&XCAFDoc_DocumentTool::ColorTool);

  py::class_<XCAFDoc_ShapeMapTool, opencascade::handle<XCAFDoc_ShapeMapTool>, TDF_Attribute>(m,"XCAFDoc_ShapeMapTool")
    .def(py::init<>())
    .def_static("GetID", &XCAFDoc_ShapeMapTool::GetID);

  py::class_<XCAFDoc_Location, opencascade::handle<XCAFDoc_Location>, TDF_Attribute>(m, "XCAFDoc_Location")
    .def(py::init<>())
    .def("Get",&XCAFDoc_Location::Get)
    .def_static("GetID", &XCAFDoc_Location::GetID);

  py::class_<XCAFDoc_ShapeTool, opencascade::handle<XCAFDoc_ShapeTool>>(m,"XCAFDoc_ShapeTool")
    .def(py::init<>())
    .def("BaseLabel", &XCAFDoc_ShapeTool::BaseLabel)
    .def("Dump",[](XCAFDoc_ShapeTool &st) { py::scoped_ostream_redirect output; st.Dump(std::cout);})
    .def("FindComponent",&XCAFDoc_ShapeTool::FindComponent)
    .def("FindShape",[](XCAFDoc_ShapeTool &st,
                        const TopoDS_Shape &shape,
                        TDF_Label &label,
                        const Standard_Boolean findInstance) {return st.FindShape(shape,label,findInstance);})
    .def("FindShape",[](XCAFDoc_ShapeTool &st,
                        const TopoDS_Shape &shape,
                        const Standard_Boolean findInstance) {return st.FindShape(shape,findInstance);})
    .def("GetComponents", [](XCAFDoc_ShapeTool &st, const TDF_Label &label, TDF_LabelSequence &labels, const Standard_Boolean getsubchilds) {st.GetComponents(label,labels,getsubchilds);})
    .def("GetReferredShape", [](XCAFDoc_ShapeTool &st, const TDF_Label &label1, TDF_Label &label2) {st.GetReferredShape(label1,label2);})
    .def("GetShape",[](XCAFDoc_ShapeTool &st,const TDF_Label &label, TopoDS_Shape &shape ) {return st.GetShape(label,shape);})
    .def("GetShape",[](XCAFDoc_ShapeTool &st,const TDF_Label &label) {return st.GetShape(label);})
    .def("GetShapes", &XCAFDoc_ShapeTool::GetShapes)
    .def("GetFreeShapes", &XCAFDoc_ShapeTool::GetFreeShapes)
    .def("GetSubShapes",&XCAFDoc_ShapeTool::GetSubShapes)
    .def("GetUsers",&XCAFDoc_ShapeTool::GetUsers)
    .def("ID",&XCAFDoc_ShapeTool::ID)
    .def("IsAssembly", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsAssembly(label);})
    .def("IsComponent", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsComponent(label);})
    .def("IsCompound", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsCompound(label);})
    .def("IsFree", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsFree(label);})
    .def("IsReference", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsReference(label);})
    .def("IsShape", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsShape(label);})
    .def("IsSimpleShape", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsSimpleShape(label);})
    .def("IsSubShape", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsSubShape(label);})
    .def("IsTopLevel", [](XCAFDoc_ShapeTool &st, const TDF_Label &label) {return st.IsTopLevel(label);})
    .def("NewShape",&XCAFDoc_ShapeTool::NewShape)
    .def("Search",&XCAFDoc_ShapeTool::Search)
    .def("SearchUsingMap", &XCAFDoc_ShapeTool::SearchUsingMap)
    .def("SetShape",&XCAFDoc_ShapeTool::SetShape);
}