#ifndef CONS_H
#define CONS_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include "Vector.h"
#include "Wedge.h"
#include "G4Plane.h"
#include <cmath>

class Cons: public SolidBase{
public:
  Cons(std::string name, double _pRmin1, double  _pRmax1,  double _pRmin2, double _pRmax2,  double _pDz,  double _pSPhi,  double _pDPhi):
      SolidBase(name,"Cons"), pRmin1(_pRmin1),  pRmax1(_pRmax1),  pRmin2(_pRmin2), pRmax2(_pRmax2),  pDz(_pDz),  pSPhi(_pSPhi),  pDPhi(_pDPhi)
  {
    SetMesh(CSGMesh::ConstructCons( pRmin1,  pRmax1,  pRmin2, pRmax2,  pDz,  pSPhi,  pDPhi));
  }
  const double pRmin1,  pRmax1,  pRmin2, pRmax2,  pDz,  pSPhi,  pDPhi;
};
#endif
