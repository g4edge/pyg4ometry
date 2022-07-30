#include "oce.h"

#include <NCollection_Vector.hxx>
#include <STEPCAFControl_Reader.hxx>
#include <TDataStd_Name.hxx>
#include <TDF_Label.hxx>
#include <NCollection_Sequence.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Face.hxx>
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

TDF_Label XCAF::shapeTool_BaseLabel() {
  return aShapeTool->BaseLabel();
}

void XCAF::shapeTool_Dump() {
    aShapeTool->Dump(std::cout);
}

StepFile::StepFile() {

  hApp = XCAFApp_Application::GetApplication();
  hApp->NewDocument(TCollection_ExtendedString("MDTV-CAF"), hDoc);
}

StepFile::~StepFile() {}

void StepFile::loadFile(std::string fileName) {
  STEPCAFControl_Reader aReader;
  aReader.SetColorMode(true);
  aReader.SetNameMode(true);
  aReader.SetLayerMode(true);

  aReader.ReadFile(fileName.c_str());

  aReader.Transfer(hDoc);

  aShapeTool = XCAFDoc_DocumentTool::ShapeTool(hDoc->Main());
  aColorTool = XCAFDoc_DocumentTool::ColorTool(hDoc->Main());
}

void StepFile::loadShapes() {
  TDF_LabelSequence labels;
  //aShapeTool->Dump(std::cout);
  aShapeTool->GetShapes(labels);
  for(auto label : labels) {
    auto shape = aShapeTool->GetShape(label);
    std::cout << label << std::endl;
    std::cout << shape.ShapeType() << std::endl;

    const Standard_Real aLinearDeflection   = 0.01;
    const Standard_Real anAngularDeflection = 0.5;
    BRepMesh_IncrementalMesh aMesher (shape, aLinearDeflection, Standard_False, anAngularDeflection, Standard_True);
    const Standard_Integer aStatus = aMesher.GetStatusFlags();
    aMesher.Perform();
    std::cout << aStatus << std::endl;

    TopExp_Explorer exFace;
    int i = 0;
    for (exFace.Init(shape, TopAbs_FACE); exFace.More(); exFace.Next()) {
      const TopoDS_Face& faceref = static_cast<const TopoDS_Face &>(exFace.Current());
      //mesh->extractFaceMesh(faceref);
      i++;
    }
    std::cout << "faces " << i << std::endl;

    auto stlWriter = StlAPI_Writer ();
    stlWriter.Write(shape,"test.stl");

  }
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(oce, m) {

  py::class_<XCAFApp_Application>(m,"XCAFApp_Application");

  py::class_<TDocStd_Document>(m,"TDocStd_Document");

  py::class_<Message_ProgressRange>(m,"Message_ProgressRange")
    .def(py::init<>());

  py::class_<TCollection_ExtendedString>(m,"TCollection_ExtendedString")
    .def("Print",[](TCollection_ExtendedString string) {string.Print(std::cout);});

  py::class_<Standard_GUID>(m,"Standard_GUID");

  py::class_<TDF_Attribute>(m,"TDF_Attribute");


  py::class_<TDataStd_Name>(m, "TDataStd_Name")
    .def(py::init<>())
    .def("Get",[](TDataStd_Name name) {return name.Get();})
    .def_static("GetID",&TDataStd_Name::GetID)
    .def("Dump",[](TDataStd_Name &name) { name.Dump(std::cout);});

  py::class_<Handle(TDataStd_Name)>(m, "Handle_TDataStd_Name")
    .def(py::init<>())
    .def("Get",[](Handle(TDataStd_Name) name) {return name->Get();})
    .def_static("GetID",&TDataStd_Name::GetID)
    .def("Dump",[](Handle(TDataStd_Name) &name) { name->Dump(std::cout);});

  py::class_<TDF_Label>(m,"TDF_Label")
     .def(py::init<>())
    .def("Depth", &TDF_Label::Depth)
    .def("Father", &TDF_Label::Father)
    .def("FindAttribute", [](TDF_Label label, Standard_GUID & guid, Handle(TDF_Attribute)& attribute) {return label.FindAttribute(guid,attribute);})
    .def("FindAttribute", [](TDF_Label label, Standard_GUID & guid, Handle(TDataStd_Name)& attribute) {return label.FindAttribute(guid,attribute);})
    .def("FindChild", &TDF_Label::FindChild)
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
    .def("Dump",[](TDF_Label &label) { label.Dump(std::cout);})
    .def("EntryDump",[](TDF_Label &label) { label.EntryDump(std::cout);});

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

  py::class_<TopLoc_Location>(m,"TopLoc_Location");
  py::class_<Handle(TopoDS_TShape)>(m,"Handle_TopoDS_TShape");

  py::class_<TopoDS_Shape>(m,"TopoDS_Shape")
    .def(py::init<>())
    .def("IsNull",&TopoDS_Shape::IsNull)
    .def("NbChildren",&TopoDS_Shape::NbChildren)
    .def("Nullify", &TopoDS_Shape::Nullify)
    .def("Location", [](TopoDS_Shape &shape) {return shape.Location();})
    .def("Location", [](TopoDS_Shape &shape,const TopLoc_Location &loc, const Standard_Boolean theRaiseExc) {return shape.Location(loc,theRaiseExc);})
    .def("ShapeType",&TopoDS_Shape::ShapeType);

  py::class_<TopExp_Explorer>(m,"TopExp_Explorer")
    .def(py::init<>())
    .def(py::init<const TopoDS_Shape &, const TopAbs_ShapeEnum, const TopAbs_ShapeEnum>())
    .def("Init",&TopExp_Explorer::Init)
    .def("More",&TopExp_Explorer::More)
    .def("Next",&TopExp_Explorer::Next)
    .def("Value",&TopExp_Explorer::Value)
    .def("Current",&TopExp_Explorer::Current)
    .def("ReInit",&TopExp_Explorer::ReInit)
    .def("ExploredShape",&TopExp_Explorer::ExploredShape)
    .def("Depth",&TopExp_Explorer::Depth)
    .def("Clear",&TopExp_Explorer::Clear);

  py::class_<Handle(XCAFDoc_ShapeTool)>(m,"XCAFDoc_ShapeTool")
    .def("BaseLabel", [](Handle(XCAFDoc_ShapeTool) &st) { return st->BaseLabel();})
    .def("Dump",[](Handle(XCAFDoc_ShapeTool) &st) { st->Dump(std::cout);})
    .def("FindShape",[](Handle(XCAFDoc_ShapeTool) &st,
                        const TopoDS_Shape &shape,
                        TDF_Label &label,
                        const Standard_Boolean findInstance) {return st->FindShape(shape,label,findInstance);})
    .def("FindShape",[](Handle(XCAFDoc_ShapeTool) &st,
                        const TopoDS_Shape &shape,
                        const Standard_Boolean findInstance) {return st->FindShape(shape,findInstance);})
    .def("GetComponents",[](Handle(XCAFDoc_ShapeTool) &st, const TDF_Label &label,TDF_LabelSequence &labelSeq) {return st->GetComponents(label,labelSeq);})
    .def("GetShape",[](Handle(XCAFDoc_ShapeTool) &st,const TDF_Label &label, TopoDS_Shape &shape ) {return st->GetShape(label,shape);})
    .def("GetShape",[](Handle(XCAFDoc_ShapeTool) &st,const TDF_Label &label) {return st->GetShape(label);})
    .def("GetShapes", [](Handle(XCAFDoc_ShapeTool) &st, TDF_LabelSequence &labelSeq) {return st->GetShapes(labelSeq);})
    .def("GetSubShapes",[](Handle(XCAFDoc_ShapeTool) &st, const TDF_Label &label,TDF_LabelSequence &labelSeq) {return st->GetSubShapes(label,labelSeq);})
    .def("GetUsers",[](Handle(XCAFDoc_ShapeTool) &st, const TDF_Label &label,TDF_LabelSequence &labelSeq) {return st->GetUsers(label,labelSeq);})
    .def("IsAssembly", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsAssembly(label);})
    .def("IsComponent", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsComponent(label);})
    .def("IsCompound", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsCompound(label);})
    .def("IsFree", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsFree(label);})
    .def("IsReference", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsReference(label);})
    .def("IsShape", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsShape(label);})
    .def("IsSimpleShape", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsSimpleShape(label);})
    .def("IsSubShape", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) {return st->IsSubShape(label);})
    .def("IsTopLevel", [](Handle(XCAFDoc_ShapeTool) &st, TDF_Label &label) { return st->IsTopLevel(label);})
    .def("Search",[](Handle(XCAFDoc_ShapeTool) &st,
                     const TopoDS_Shape & shape,
                     TDF_Label & label,
                     const Standard_Boolean findInstance = Standard_True,
                     const Standard_Boolean findComponent = Standard_True,
                     const Standard_Boolean findSubshape = Standard_True) {return st->Search(shape,label,findInstance,findComponent,findSubshape);})
    .def("SearchUsingMap", [](Handle(XCAFDoc_ShapeTool) &st,
                              const TopoDS_Shape &shape,
                              TDF_Label &label,
                              const Standard_Boolean findWithoutLoc,
                              const Standard_Boolean findSubshape) {return st->SearchUsingMap(shape,label,findWithoutLoc,findSubshape);});

  py::class_<BRepMesh_IncrementalMesh>(m,"BRepMesh_IncrementalMesh")
    .def(py::init<>())
    .def(py::init<const TopoDS_Shape &,
                  const Standard_Real,
                  const Standard_Boolean,
                  const Standard_Real,
                  const Standard_Boolean>())
    .def(py::init<const TopoDS_Shape &,
                  const IMeshTools_Parameters,
                  const Message_ProgressRange>());

  py::class_<XCAF>(m,"XCAF")
    .def(py::init<>())
    .def("loadStepFile", &XCAF::loadStepFile)
    .def("loadIGESFile", &XCAF::loadIGESFile)
    .def("loadSTLFile", &XCAF::loadSTLFile)
    .def("shapeTool", &XCAF::shapeTool)
    .def("shapeTool_BaseLabel", &XCAF::shapeTool_BaseLabel)
    .def("shapeTool_Dump", &XCAF::shapeTool_Dump);

  py::class_<StlAPI_Writer>(m,"StlAPI_Writer")
    .def(py::init<>())
    .def("Write",[](StlAPI_Writer &stlw,
                    const TopoDS_Shape &shape,
                    const Standard_CString fileName,
                    const Message_ProgressRange &processRange) {std::cout << fileName << std::endl;
                                                                stlw.Write(shape,fileName);});

  py::class_<StepFile>(m,"StepFile")
    .def(py::init<>())
    .def("loadFile", &StepFile::loadFile)
    .def("loadShapes", &StepFile::loadShapes);
}
