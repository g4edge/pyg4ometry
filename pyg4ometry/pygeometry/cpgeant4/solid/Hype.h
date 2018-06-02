#ifndef HYPE_H
#define HYPE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Hype : public SolidBase{
public:
  Hype(std:: string name, double _innerRadius,double  _outerRadius,double  _innerStereo,double  _outerStereo,double  _halfLenZ, int _nslice=16,int _nstack=16):
      SolidBase(name,"Hype"),innerRadius(_innerRadius), outerRadius(_outerRadius), innerStereo(_innerStereo), outerStereo(_outerStereo), halfLenZ(_halfLenZ), nslice(_nslice), nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructHype(innerRadius, outerRadius, innerStereo, outerStereo, halfLenZ, nslice, nstack));
  }
  const double innerRadius,  outerRadius,  innerStereo,  outerStereo,  halfLenZ;
  const int nslice, nstack;
};
#endif
