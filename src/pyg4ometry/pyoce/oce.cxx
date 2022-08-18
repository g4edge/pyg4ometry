// Older manual a little hard to track down so included here
// https://old.opencascade.com/doc/occt-7.5.0/overview/html/index.html
// https://old.opencascade.com/doc/occt-7.5.0/refman/html/index.html

#include "oce.h"

#include "Standard_Version.hxx"
#include <NCollection_Vector.hxx>
#include <STEPCAFControl_Reader.hxx>
#include <TDataStd_Name.hxx>
#include <TNaming_NamedShape.hxx>
#include <TDataStd_TreeNode.hxx>
#include <TDataStd_UAttribute.hxx>
#include <XCAFDoc_ShapeMapTool.hxx>
#include <XCAFDoc_Location.hxx>
#include <TDF_Label.hxx>
#include <TDF_Tool.hxx>
#include <gp_Trsf.hxx>
#include <TopLoc_Location.hxx>
#include <TopLoc_Datum3D.hxx>
#include <NCollection_Sequence.hxx>
#include <BRep_Tool.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_TFace.hxx>
#include <TopoDS_TWire.hxx>
// #include <Poly_MeshPurpose.hxx>
#include <Poly_Triangulation.hxx>
#include <gp_Dir.hxx>
#include <Message_ProgressRange.hxx>
#include <StlAPI_Writer.hxx>

XCAF::XCAF() {
  hApp = XCAFApp_Application::GetApplication();
  hApp->NewDocument(TCollection_ExtendedString("MDTV-CAF"), hDoc);
}

XCAF::~XCAF() {}

void XCAF::createNewDocument() {
}

void XCAF::loadStepFile(std::string fileName) {
  STEPCAFControl_Reader aReader;
  aReader.SetColorMode(true);
  aReader.SetNameMode(true);
  aReader.SetLayerMode(true);

  aReader.ReadFile(fileName.c_str());

  aReader.Transfer(hDoc);

  aShapeTool = XCAFDoc_DocumentTool::ShapeTool(hDoc->Main());
  aColorTool = XCAFDoc_DocumentTool::ColorTool(hDoc->Main());
}

void XCAF::loadSTLFile(std::string fileName) {}
void XCAF::loadIGESFile(std::string fileName) {}

Handle(XCAFDoc_ShapeTool) XCAF::shapeTool() {
  return aShapeTool;
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(oce, m) {

  py::class_<Geom_Geometry, opencascade::handle<Geom_Geometry>>(m,"Geom_Geometry");
  py::class_<Geom_Curve, opencascade::handle<Geom_Curve>, Geom_Geometry>(m,"Geom_Curve")
    .def("Value",&Geom_Curve::Value);

  py::class_<XCAFApp_Application, opencascade::handle<XCAFApp_Application>>(m,"XCAFApp_Application");

  py::class_<TDocStd_Document, opencascade::handle<TDocStd_Document>> (m,"TDocStd_Document");

  py::class_<Message_ProgressRange> (m,"Message_ProgressRange")
    .def(py::init<>());

  py::class_<TCollection_AsciiString>(m,"TCollection_AsciiString")
    .def(py::init<>());

  py::class_<TCollection_ExtendedString>(m,"TCollection_ExtendedString")
    .def(py::init<>())
    .def(py::init<const Standard_CString, const Standard_Boolean>())
    .def(py::init<const Standard_ExtString>())
    .def(py::init<const Standard_Character>())
    .def(py::init<const Standard_ExtCharacter>())
    .def(py::init<const Standard_Integer, const Standard_ExtCharacter>())
    .def(py::init<const Standard_Integer>())
    .def(py::init<const Standard_Real>())
    .def(py::init<const TCollection_ExtendedString>())
    .def(py::init<const TCollection_AsciiString &>())
    .def("Length",&TCollection_ExtendedString::Length)
    .def("Print",[](TCollection_ExtendedString &string) {py::scoped_ostream_redirect output; string.Print(std::cout);})
    .def("ToExtString",&TCollection_ExtendedString::ToExtString);

  py::class_<Standard_GUID> (m,"Standard_GUID");

  py::class_<Standard_Transient, opencascade::handle<Standard_Transient>> (m,"Standard_Transient");

  py::class_<TDF_Attribute, opencascade::handle<TDF_Attribute>, Standard_Transient> (m,"TDF_Attribute");

  py::class_<TDataStd_GenericExtString, opencascade::handle<TDataStd_GenericExtString>, TDF_Attribute>(m,"TDataStd_GenericExtString")
    .def("ID", &TDataStd_GenericExtString::ID)
    .def("Get",&TDataStd_GenericExtString::Get)
    .def("Set",&TDataStd_GenericExtString::Set);

  py::class_<TNaming_NamedShape, opencascade::handle<TNaming_NamedShape>, TDF_Attribute>(m,"TNaming_NamedShape")
    .def(py::init([](){return opencascade::handle<TNaming_NamedShape>(new TNaming_NamedShape());}))
    .def("ID", &TNaming_NamedShape::ID)
    .def("Dump",[](TNaming_NamedShape &name) { py::scoped_ostream_redirect output; name.Dump(std::cout);})
    .def("Get",&TNaming_NamedShape::Get)
    .def_static("GetID",&TNaming_NamedShape::GetID);

  py::class_<TDF_TagSource, opencascade::handle<TDF_TagSource>, TDF_Attribute>(m,"TDF_TagSource")
    .def(py::init<>())
    .def("Get",&TDF_TagSource::Get)
    .def_static("GetID",&TDF_TagSource::GetID);

  py::class_<TDataStd_TreeNode, opencascade::handle<TDataStd_TreeNode>, TDF_Attribute>(m,"TDataStd_TreeNode")
    .def(py::init<>())
    .def("ID",&TDataStd_TreeNode::ID)
    .def("DumpJson",[](TDataStd_TreeNode &treeNode) {treeNode.DumpJson(std::cout);});

  py::class_<TDataStd_UAttribute, opencascade::handle<TDataStd_UAttribute>, TDF_Attribute>(m,"TDataStd_UAttribute")
    .def(py::init<>())
    .def("ID",&TDataStd_UAttribute::ID);

  py::class_<XCAFDoc_ShapeMapTool, opencascade::handle<XCAFDoc_ShapeMapTool>, TDF_Attribute>(m,"XCAFDoc_ShapeMapTool")
    .def(py::init<>())
    .def_static("GetID", &XCAFDoc_ShapeMapTool::GetID);

  py::class_<XCAFDoc_Location, opencascade::handle<XCAFDoc_Location>, TDF_Attribute>(m, "XCAFDoc_Location")
    .def(py::init<>())
    .def("Get",&XCAFDoc_Location::Get)
    .def_static("GetID", &XCAFDoc_Location::GetID);

  py::class_<TDataStd_Name,opencascade::handle<TDataStd_Name>, TDataStd_GenericExtString>(m, "TDataStd_Name")
    .def(py::init([](){return opencascade::handle<TDataStd_Name>(new TDataStd_Name());}))
    .def("ID", &TDataStd_Name::ID)
    .def("Dump",[](TDataStd_Name &name) { py::scoped_ostream_redirect output; name.Dump(std::cout);})
    .def_static("GetID",&TDataStd_Name::GetID);

  py::class_<TDF_Label> (m,"TDF_Label")
    .def(py::init<>())
    .def("Depth", &TDF_Label::Depth)
    .def("Father", &TDF_Label::Father)
    .def("FindAttribute", [](TDF_Label &label, const Standard_GUID & guid, opencascade::handle<TDF_Attribute> &attribute) { auto ret = label.FindAttribute(guid,attribute); return py::make_tuple(ret, attribute);})
    .def("FindAttribute", [](TDF_Label &label, const Standard_GUID & guid, const Standard_Integer aTransaction, opencascade::handle<TDataStd_Name> &attribute) { auto ret =  label.FindAttribute(guid,aTransaction,attribute); return py::make_tuple(ret,attribute);})
    .def("FindChild", [](TDF_Label &label, const Standard_Integer tag, const Standard_Boolean create) {auto retLabel = label.FindChild(tag,create); return py::make_tuple(!retLabel.IsNull(), retLabel);})
    .def("HasAttribute", &TDF_Label::HasAttribute)
    .def("HasChild", &TDF_Label::HasChild)
    .def("IsDifferent", &TDF_Label::IsDifferent)
    .def("IsAttribute",&TDF_Label::IsAttribute)
    .def("IsEqual", &TDF_Label::IsEqual)
    .def("IsNull", &TDF_Label::IsNull)
    .def("IsRoot",&TDF_Label::IsRoot)
    .def("NewChild", &TDF_Label::NewChild)
    .def("NbAttributes", &TDF_Label::NbAttributes)
    .def("NbChildren", &TDF_Label::NbChildren)
    .def("Nullify", &TDF_Label::Nullify)
    .def("Root", &TDF_Label::Root)
    .def("Tag", &TDF_Label::Tag)
    .def("Transaction", &TDF_Label::Transaction)
    .def("Dump",[](TDF_Label &label) { py::scoped_ostream_redirect output; label.Dump(std::cout);})
    .def("EntryDump",[](TDF_Label &label) { py::scoped_ostream_redirect output; label.EntryDump(std::cout);});

  py::class_<NCollection_Sequence<TDF_Label>::iterator>(m,"TDF_LabelSequence_Iterator");

  py::class_<TDF_LabelSequence>(m,"TDF_LabelSequence")
    .def(py::init<>())
    .def("Size",&TDF_LabelSequence::Size)
    .def("begin",&TDF_LabelSequence::begin)
    .def("end",&TDF_LabelSequence::end)
    .def("Dump",[](TDF_LabelSequence &ls) { return;})
    .def("Value",&TDF_LabelSequence::Value)
    .def("__iter__",[](const TDF_LabelSequence &s) { return py::make_iterator(s.begin(), s.end()); }, py::keep_alive<0, 1>())
    .def("__call__",[](TDF_LabelSequence &ls, Standard_Integer i) { return ls(i);});

  py::class_<TDF_Tool>(m,"TDF_Tool")
    .def_static("Entry",&TDF_Tool::Entry);

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

  py::class_<gp_XYZ>(m,"gp_XYZ")
    .def(py::init<>())
    .def("DumpJson",[](gp_XYZ &gpxyz) {py::scoped_ostream_redirect output; gpxyz.DumpJson(std::cout);});

  py::class_<gp_Trsf>(m,"gp_Trsf")
    .def(py::init<>())
    .def("TranslationPart",&gp_Trsf::TranslationPart)
    .def("DumpJson",[](gp_Trsf &gpt) {py::scoped_ostream_redirect output; gpt.DumpJson(std::cout);});

  py::class_<TopLoc_Location>(m,"TopLoc_Location")
    .def(py::init<>())
    .def("FirstDatum",[](TopLoc_Location &location) {return location.FirstDatum();})
    .def("ShallowDump",[](TopLoc_Location &location) {py::scoped_ostream_redirect output; location.ShallowDump(std::cout);})
    .def("Transformation",[](TopLoc_Location &location) {return location.Transformation();});

  py::class_<TopLoc_Datum3D, opencascade::handle<TopLoc_Datum3D>, Standard_Transient>(m,"TopLoc_Datum3D")
    .def(py::init<>())
    .def("ShallowDump",[](TopLoc_Location &location) {py::scoped_ostream_redirect output; location.ShallowDump(std::cout);});

  py::class_<TopoDS>(m,"TopoDS")
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

  py::class_<gp_Dir>(m,"gp_Dir")
    .def(py::init<>());

  py::class_<gp_Pnt>(m,"gp_Pnt")
    .def(py::init<>())
    .def("X",&gp_Pnt::X)
    .def("Y",&gp_Pnt::Y)
    .def("Z",&gp_Pnt::Z);

  py::class_<Poly_Triangle>(m,"Poly_Triangle")
    .def(py::init<>())
    .def(py::init<const Standard_Integer, const Standard_Integer, const Standard_Integer>())
    .def("Set",[](Poly_Triangle &tri, const Standard_Integer n1, const Standard_Integer n2, const Standard_Integer n3) {tri.Set(n1,n2,n3);})
    .def("Set",[](Poly_Triangle &tri, const Standard_Integer index, const Standard_Integer node) {tri.Set(index,node);})
    .def("Get",[](Poly_Triangle &tri) {Standard_Integer n1, n2, n3; tri.Get(n1,n2,n3); return py::make_tuple(n1,n2,n3);})
    .def("Value", &Poly_Triangle::Value)
    .def("__call__",[](Poly_Triangle &tri, const Standard_Integer index) {return tri(index);});

  py::class_<Poly_Triangulation, opencascade::handle<Poly_Triangulation>, Standard_Transient>(m, "Poly_Triangulation")
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def(py::init<>())
    .def(py::init<const Standard_Integer, const Standard_Integer, const Standard_Boolean, const Standard_Boolean>())
#else
    .def(py::init<const Standard_Integer, const Standard_Integer, const Standard_Boolean>())
#endif

    .def("Deflection",[](Poly_Triangulation &pt){return pt.Deflection();})
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("HasGeometry",&Poly_Triangulation::HasGeometry)
#endif
    .def("HasNormals",&Poly_Triangulation::HasNormals)
    .def("HasUVNodes",&Poly_Triangulation::HasUVNodes)
    .def("NbNodes",&Poly_Triangulation::NbNodes)
    .def("NbTriangles",&Poly_Triangulation::NbTriangles)
    .def("Node",&Poly_Triangulation::Node)
    .def("Normal",[](Poly_Triangulation &pt, Standard_Integer i) {return pt.Normal(i);})
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("SetNode",&Poly_Triangulation::SetNode)
    .def("SetTriangle",&Poly_Triangulation::SetTriangle)
#endif
    .def("Triangle",&Poly_Triangulation::Triangle)
    .def("UVNode",&Poly_Triangulation::Node);

  // Copied from Poly_MeshPurpose.hxx
  enum Poly_MeshPurpose {
    Poly_MeshPurpose_NONE = 0 , Poly_MeshPurpose_Calculation = 0x0001 , Poly_MeshPurpose_Presentation = 0x0002 , Poly_MeshPurpose_Active = 0x0004 ,
    Poly_MeshPurpose_Loaded = 0x0008 , Poly_MeshPurpose_AnyFallback = 0x0010 , Poly_MeshPurpose_USER = 0x0020
  };

  py::enum_<Poly_MeshPurpose>(m,"Poly_MeshPurpose")
    .value("Poly_MeshPurpose_NONE", Poly_MeshPurpose::Poly_MeshPurpose_NONE)
    .value("Poly_MeshPurpose_Calculation", Poly_MeshPurpose::Poly_MeshPurpose_Calculation)
    .value("Poly_MeshPurpose_Presentation", Poly_MeshPurpose::Poly_MeshPurpose_Presentation)
    .value("Poly_MeshPurpose_Active", Poly_MeshPurpose::Poly_MeshPurpose_Active)
    .value("Poly_MeshPurpose_Loaded", Poly_MeshPurpose::Poly_MeshPurpose_Loaded)
    .value("Poly_MeshPurpose_AnyFallback", Poly_MeshPurpose::Poly_MeshPurpose_AnyFallback)
    .value("Poly_MeshPurpose_USER", Poly_MeshPurpose::Poly_MeshPurpose_USER)
    .export_values();

  py::class_<BRep_Tool>(m,"BRep_Tool")
    .def_static("Curve",[](const TopoDS_Edge &E, TopLoc_Location &L,
                           Standard_Real &First, Standard_Real &Last)
        {
            auto ret = BRep_Tool::Curve(E,L,First,Last);
            return py::make_tuple(ret,L,First,Last);
        })
    .def_static("Triangulation",&BRep_Tool::Triangulation);

  py::class_<StlAPI_Writer>(m,"StlAPI_Writer")
    .def(py::init<>())
    .def("Write",[](StlAPI_Writer &stlw,
                    const TopoDS_Shape &shape,
                    const Standard_CString fileName,
                    const Message_ProgressRange &processRange) {py::scoped_ostream_redirect output;
                                                                std::cout << fileName << std::endl;
                                                                stlw.Write(shape,fileName);});

  py::class_<XCAF>(m,"XCAF")
    .def(py::init<>())
    .def("loadStepFile", &XCAF::loadStepFile)
    .def("loadIGESFile", &XCAF::loadIGESFile)
    .def("loadSTLFile", &XCAF::loadSTLFile)
    .def("shapeTool", &XCAF::shapeTool);
}
