#ifndef TRD_H
#define TRD_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Trd : public SolidBase{
public:
  Trd(std::string name,double _x1,double _x2,double _y1,double _y2,double _z):
      SolidBase(name,"Trd"),x1(_x1),x2(_x2),y1(_y1),y2(_y2),z(_z)
  {
    SetMesh(CSGMesh::ConstructTrd(x1,x2,y1,y2,z));
  }
  const double x1,x2,y1,y2,z;
};
#endif
