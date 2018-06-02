#ifndef ELLIPTICALCONE_H
#define ELLIPTICALCONE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class EllipticalCone : public SolidBase{
public:
  EllipticalCone(std::string name,double _pxSemiAxis,double _pySemiAxis,double _zMax,double _pzTopCut,int _nslice,int _nstack):
      SolidBase(name,"EllipticalCone"),pxSemiAxis(_pxSemiAxis),pySemiAxis(_pySemiAxis),zMax(_zMax),pzTopCut(_pzTopCut),nslice(_nslice),nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructEllipticalCone(pxSemiAxis, pySemiAxis, zMax, pzTopCut, nslice, nstack));
  }
  const double pxSemiAxis,pySemiAxis,zMax,pzTopCut;
  const int nslice, nstack;
};
#endif
