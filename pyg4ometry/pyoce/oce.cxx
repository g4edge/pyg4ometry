#include "oce.h"

#include <NCollection_Vector.hxx>
#include <STEPCAFControl_Reader.hxx>

#include <TDF_Label.hxx>
#include <NCollection_Sequence.hxx>

#include <BRepMesh_IncrementalMesh.hxx>

#include <TopExp_Explorer.hxx>
#include <TopoDS_Face.hxx>

#include <StlAPI_Writer.hxx>

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

    const Standard_Real aLinearDeflection   = 0.001;
    const Standard_Real anAngularDeflection = 0.05;
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
  py::class_<StepFile>(m,"StepFile")
    .def(py::init<>())
    .def("loadFile", &StepFile::loadFile)
    .def("loadShapes", &StepFile::loadShapes);

}
