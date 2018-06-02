#ifndef PARABOLOID_H
#define PARABOLOID_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Paraboloid : public SolidBase{
public:
  Paraboloid(std::string name,double _pDz,double _pR1,double _pR2,int _nstack=8,int _nslice=16):
      SolidBase(name,"Paraboloid"),pDz(_pDz),pR1(_pR1),pR2(_pR2),nstack(_nstack),nslice(_nslice)
  {
    SetMesh(CSGMesh::ConstructParaboloid(pDz, pR1, pR2, nstack, nslice));
  }
  const double pDz, pR1, pR2;
  const int nstack, nslice;
};
#endif
