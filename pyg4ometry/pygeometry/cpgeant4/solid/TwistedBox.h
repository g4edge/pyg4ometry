#ifndef TWISTED_BOX_H
#define TWISTED_BOX_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include <cmath>

class TwistedBox : public SolidBase{
public:
  TwistedBox(std::string name,double _twistedangle, double _pDx, double _pDy, double _pDz, int _refine):
      SolidBase(name,"twistedbox"), twistedangle(_twistedangle),  pDx(_pDx),  pDy(_pDy),  pDz(_pDz), refine(_refine)
  {
    SetMesh(CSGMesh::ConstructTwistedBox(twistedangle,  pDx,  pDy,  pDz,refine));
  }
  const double twistedangle, pDx, pDy, pDz;
  const int refine;
};
#endif
