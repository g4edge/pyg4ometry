#ifndef TUBS_H
#define TUBS_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include "Wedge.h"
#include <cmath>

class Tubs : public SolidBase{
public:
    Tubs(std::string name,double _pRmin,double _pRmax,double _pDz,double _pSPhi,double _pDPhi):
            SolidBase(name,"Tubs"), pRmin(_pRmin), pRmax(_pRmax), pDz(_pDz), pSPhi(_pSPhi), pDPhi(_pDPhi)
    {
        SetMesh(CSGMesh::ConstructTubs(pRmin, pRmax, pDz, pSPhi, pDPhi));
    }
    const double pRmin, pRmax, pDz, pSPhi, pDPhi;
};
#endif
