#ifndef SPHERE_H
#define SPHERE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Sphere : public SolidBase{
public:
  Sphere(std::string name,double _pRmin,double _pRmax,double _pSPhi,double _pDPhi,double _pSTheta,double _pDTheta,int _nslice = 8, int _nstack = 8):
      SolidBase(name,"Sphere"),pRmin(_pRmin),pRmax(_pRmax),pSPhi(_pSPhi),pDPhi(_pDPhi),pSTheta(_pSTheta),pDTheta(_pDTheta),nslice(_nslice),nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructSphere( pRmin, pRmax, pSPhi, pDPhi, pSTheta, pDTheta, nslice,  nstack));
  }
  const double pRmin, pRmax,pSPhi,pDPhi,pSTheta,pDTheta;
  const int nslice, nstack;
};
#endif
