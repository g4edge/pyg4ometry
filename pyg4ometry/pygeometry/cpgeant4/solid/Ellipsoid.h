#ifndef ELLIPSOID_H
#define ELLIPSOID_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Ellipsoid : public SolidBase{
public:
  Ellipsoid(std::string name, double _pxSemiAxis,double _pySemiAxis,double _pzSemiAxis,double _pzBottomCut,double _pzTopCut,int _nslice = 8,int _nstack = 8):
      SolidBase(name,"Ellipsoid"),pxSemiAxis(_pxSemiAxis),pySemiAxis(_pySemiAxis), pzSemiAxis(_pzSemiAxis), pzBottomCut(_pzBottomCut), pzTopCut(_pzTopCut),nslice(_nslice),nstack(_nstack)
  {
    SetMesh(CSGMesh::ConstructEllipsoid(pxSemiAxis, pySemiAxis, pzSemiAxis, pzBottomCut, pzTopCut,nslice,nstack));
  }
  const double pxSemiAxis, pySemiAxis, pzSemiAxis, pzBottomCut, pzTopCut;
  const int nslice, nstack;
};
#endif
