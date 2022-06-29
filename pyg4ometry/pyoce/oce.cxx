#include "oce.h"

#include <TDocStd_Document.hxx>
#include <NCollection_Vector.hxx>
#include <XCAFApp_Application.hxx>
#include <STEPCAFControl_Reader.hxx>

StepFile::StepFile() {
  Handle(TDocStd_Document) hDoc;
  Handle(XCAFApp_Application) hApp = XCAFApp_Application::GetApplication();

  hApp->NewDocument(TCollection_ExtendedString("MDTV-CAF"), hDoc);

  STEPCAFControl_Reader aReader;
  aReader.SetColorMode(true);
  aReader.SetNameMode(true);
  aReader.SetLayerMode(true);

  aReader.ReadFile("test.step");

  aReader.Transfer(hDoc);
}

StepFile::~StepFile() {}


/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(oce, m) {
  py::class_<StepFile>(m,"StepFile")
    .def(py::init<>());
}
