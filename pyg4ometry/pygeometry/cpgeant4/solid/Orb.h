#ifndef ORB_H
#define ORB_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Orb : public SolidBase{
public:
  Orb(std::string name,double _pRmax):
      SolidBase(name,"Orb"),pRmax(_pRmax)
  {
    SetMesh(CSGMesh::ConstructOrb(pRmax));
  }
  const double pRmax;
};
#endif
