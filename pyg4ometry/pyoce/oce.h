#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <string>

#include <TDocStd_Document.hxx>
#include <XCAFApp_Application.hxx>
#include <XCAFDoc_DocumentTool.hxx>
#include <XCAFDoc_ShapeTool.hxx>
#include <XCAFDoc_ColorTool.hxx>

class XCAF {
 public:
  XCAF();
  ~XCAF();
  void createNewDocument();
  void loadStepFile(std::string fileName);
  void loadSTLFile(std::string fileName);
  void loadIGESFile(std::string fileName);

  Handle(XCAFDoc_ShapeTool) shapeTool();

  void shapeTool_Dump();
  TDF_Label shapeTool_BaseLabel();

 protected :
  Handle(TDocStd_Document)    hDoc;
  Handle(XCAFApp_Application) hApp;

  Handle(XCAFDoc_ShapeTool) aShapeTool;
  Handle(XCAFDoc_ColorTool) aColorTool;

};

class StepFile {
 public :
  StepFile();
  ~StepFile();
  void loadFile(std::string fileName);
  void loadShapes();

 protected :
  Handle(TDocStd_Document)    hDoc;
  Handle(XCAFApp_Application) hApp;

  Handle(XCAFDoc_ShapeTool) aShapeTool;
  Handle(XCAFDoc_ColorTool) aColorTool;
};



