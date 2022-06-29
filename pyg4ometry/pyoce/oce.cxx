#include "oce.h"

#include <NCollection_Vector.hxx>
#include <STEPCAFControl_Reader.hxx>

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
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(oce, m) {
  py::class_<StepFile>(m,"StepFile")
    .def(py::init<>())
    .def("loadFile", &StepFile::loadFile);

}
