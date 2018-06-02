#ifndef POLYCONE_H
#define POLYCONE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Polycone : public SolidBase{
public:
  Polycone(std::string name,double _pSPhi,double _pDPhi,std::vector<double> _pZpl,std::vector<double> _pRMin,std::vector<double> _pRMax,int _nslice=16):
      SolidBase(name,"Polycone"), pSPhi(_pSPhi), pDPhi(_pDPhi), pZpl(_pZpl), pRMin(_pRMin), pRMax(_pRMax), nslice(_nslice)
  {
    SetMesh(CSGMesh::ConstructPolycone(pSPhi, pDPhi, pZpl, pRMin, pRMax, nslice));
  }
  const double pSPhi, pDPhi;
  const std::vector<double> pZpl, pRMin, pRMax;
  const int nslice;
};
#endif
