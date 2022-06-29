#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <string>

#include <TDocStd_Document.hxx>
#include <XCAFApp_Application.hxx>
#include <XCAFDoc_DocumentTool.hxx>
#include <XCAFDoc_ShapeTool.hxx>
#include <XCAFDoc_ColorTool.hxx>

class StepFile {
 public :
  StepFile();
  ~StepFile();
  void loadFile(std::string fileName);

 protected :
  Handle(TDocStd_Document)    hDoc;
  Handle(XCAFApp_Application) hApp;

  Handle(XCAFDoc_ShapeTool) aShapeTool;
  Handle(XCAFDoc_ColorTool) aColorTool;
};



