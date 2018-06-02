#ifndef CUT_TUBS_H
#define CUT_TUBS_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include "Vector.h"
#include "Tubs.h"
#include "G4Plane.h"

class CutTubs : public SolidBase{
public:
  CutTubs(std:: string name,double _pRmin,double _pRmax,double _pDz,double _pSPhi,double _pDPhi,Vector* _pLowNorm,Vector* _pHighNorm):
      SolidBase(name,"Cuttubs"),pRmin(_pRmin), pRmax(_pRmax), pDz(_pDz), pSPhi(_pSPhi), pDPhi(_pDPhi)
  {
    pLowNorm = _pLowNorm;
    pHighNorm = _pHighNorm;
    SetMesh(CSGMesh::ConstructCutTubs(pRmin, pRmax, pDz, pSPhi, pDPhi, pLowNorm, pHighNorm));
  }
  const double pRmin, pRmax, pDz, pSPhi, pDPhi;
  Vector* pLowNorm;
  Vector* pHighNorm;
};
#endif
