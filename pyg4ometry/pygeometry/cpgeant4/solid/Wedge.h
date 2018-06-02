#ifndef WEDGE_H
#define WEDGE_H
#include "CSGMesh.h"
#include "SolidBase.h"
#include "Vertex.h"
#include "Vector.h"
#include "Polygon.h"
#include <cmath>
#include <vector>

class Wedge : public SolidBase{
public:
    Wedge(std::string name,double _pRMax = 1000,double _pSPhi=0,double _pDPhi=1.5,double _halfzlength=10000):
            SolidBase(name,"Wedge"),pRMax(_pRMax),pSPhi(_pSPhi),pDPhi(_pDPhi),halfzlength(_halfzlength){
        SetMesh(CSGMesh::ConstructWedge(pRMax,pSPhi,pDPhi,halfzlength));
    }
    const double pRMax,pSPhi,pDPhi,halfzlength;
};

#endif
