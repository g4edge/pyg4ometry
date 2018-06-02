#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Box: public SolidBase
{
public:
  Box(std::string name, double _px, double _py, double _pz):
    SolidBase(name,"Box"),px(_px),py(_py),pz(_pz){
      SetMesh(CSGMesh::ConstructBox(px,py,pz));
    }
  const double px, py, pz;
};

CSG* CSGMesh::ConstructBox(double px,double py,double pz){
  CSG* mesh = Solids::Box(px,py,pz);
}
