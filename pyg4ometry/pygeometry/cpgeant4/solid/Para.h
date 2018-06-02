#ifndef PARA_H
#define PARA_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Para : public SolidBase{
public:
  Para(std::string name,double _pDx,double _pDy,double _pDz,double _pAlpha,double _pTheta,double _pPhi):
      SolidBase(name,"Para"),pDx(_pDx),pDy(_pDy),pDz(_pDz),pAlpha(_pAlpha),pTheta(_pTheta),pPhi(_pPhi)
  {
    SetMesh(CSGMesh::ConstructPara(pDx,pDy,pDz,pAlpha,pTheta,pPhi));
  }
  const double pDx,pDy,pDz,pAlpha,pTheta,pPhi;
};
#endif
