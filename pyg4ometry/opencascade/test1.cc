#include <BRepTools.hxx> 

#include <STEPControl_Reader.hxx> 

#include <TopoDS.hxx>
#include <TopoDS_Solid.hxx>
#include <TopoDS_Shape.hxx> 
#include <TopExp.hxx>
#include <TopTools_IndexedMapOfShape.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Compound.hxx>


#include <iostream>

int main(int argc, char* argv[]) {

  if(argc != 2) {
    std::cout << "Please profile a CAD (step) file" << std::endl;
    std::cout << "Usage : " << argv[0] << " filename.(stp/step)" << std::endl;
    exit(1);
  }
  char *fileName = argv[1];

  STEPControl_Reader reader; 
  IFSelect_ReturnStatus fileStat = reader.ReadFile(fileName);
  std::cout << "info> fileStat " << fileStat << std::endl;

  reader.TransferRoots();
  Standard_Integer nbRoots = reader.NbRootsForTransfer();
  std::cout << "info> nbRoots " << nbRoots << std::endl;

  TopoDS_Shape shape = reader.OneShape();
  TopTools_IndexedMapOfShape mapOfShapes;
  TopExp::MapShapes(shape,TopAbs_SOLID,mapOfShapes);
  std::cout <<  "info> solids found in STEP file " << mapOfShapes.Extent() << std::endl;

  
  return 0;
}
