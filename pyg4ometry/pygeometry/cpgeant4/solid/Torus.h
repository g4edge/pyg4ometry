#ifndef TORUS_H
#define TORUS_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Torus : public SolidBase{
public:
  Torus(std::string name,double _pRmin,double _pRmax,double _pRtor,double _pSPhi,double _pDPhi,int _nslice=16,int _nstack=16):
      SolidBase(name,"Torus"),pRmin(_pRmin), pRmax(_pRmax), pRtor(_pRtor), pSPhi(_pSPhi), pDPhi(_pDPhi),nslice(_nslice),nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructTorus(pRmin, pRmax, pRtor, pSPhi, pDPhi,nslice,nstack));
  }
  const double pRmin, pRmax, pRtor, pSPhi, pDPhi;
  const int nslice, nstack;
};
#endif
