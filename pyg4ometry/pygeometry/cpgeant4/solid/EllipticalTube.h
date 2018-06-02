#ifndef ELLIPTICALTUBE_H
#define ELLIPTICALTUBE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class EllipticalTube : public SolidBase{
public:
  EllipticalTube(std::string name,double _pDx,double _pDy,double _pDz,int _nslice=16,int _nstack=16):
      SolidBase(name,"EllipticalTube"),pDx(_pDx),pDy(_pDy),pDz(_pDz),nslice(_nslice),nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructEllipticalTube(pDx, pDy, pDz, nslice, nstack));
  }
  const double pDx,pDy,pDz;
  const int nslice, nstack;
};
#endif
