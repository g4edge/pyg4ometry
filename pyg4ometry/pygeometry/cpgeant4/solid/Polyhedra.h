#ifndef POLYHEDRA_H
#define POLYHEDRA_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include <vector>

class Polyhedra : public SolidBase{
public:
  Polyhedra(std::string name,double _phiStart, double _phiTotal,int _numSide,int _numZPlanes,std::vector<double> _zPlane,std::vector<double> _rInner,std::vector<double> _rOuter):
      SolidBase(name,"Polyhedra"),phiStart(_phiStart),phiTotal(_phiTotal),numSide(_numSide),numZPlanes(_numZPlanes),zPlane(_zPlane),rInner(_rInner),rOuter(_rOuter)
  {
    SetMesh(CSGMesh::ConstructPolyhedra(phiStart,phiTotal,numSide,numZPlanes,zPlane,rInner,rOuter));
  }
  const double phiStart, phiTotal;
  const int numSide,numZPlanes;
  const std::vector<double> zPlane, rInner, rOuter;
};
#endif
