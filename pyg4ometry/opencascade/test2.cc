#include <iostream>

#include <XCAFApp_Application.hxx>
#include <XCAFDoc_DocumentTool.hxx>
#include <STEPCAFControl_Reader.hxx> 

int main(int argc, char* argv[]) {

  if(argc != 2) {
    std::cout << "Please profile a CAD (step) file" << std::endl;
    std::cout << "Usage : " << argv[0] << " filename.(stp/step)" << std::endl;
    exit(1);
  }
  char *fileName = argv[1];

  STEPCAFControl_Reader reader; 
  IFSelect_ReturnStatus readstat = reader.ReadFile(fileName); 

  std::cout << "info> " << "filename=" << fileName << " readstat=" << readstat << std::endl;

  Handle(XCAFApp_Application) hApp = XCAFApp_Application::GetApplication();
  Handle(TDocStd_Document) doc;
  hApp->NewDocument(TCollection_ExtendedString("MDTV-CAF"), doc);

  if ( !reader.Transfer ( doc ) ) { 
    std::cout << "Cannot read any relevant data from the STEP file" << std::endl; 
    exit(2);
  }

  return 0;
}
