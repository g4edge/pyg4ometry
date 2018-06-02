#ifndef TRAP_H
#define TRAP_H
#include "CSGMesh.h"
#include "Solids.h"
#include "Vector.h"
#include "SolidBase.h"
#include <cmath>
#include <vector>

class Trap : public SolidBase{
public:
  Trap(std::string name, double _pDz, double _pTheta, double _pDPhi, double _pDy1, double _pDx1, double _pDx2, double _pAlp1, double _pDy2, double _pDx3, double _pDx4, double _pAlp2):
      SolidBase(name,"Trap"), pDz(_pDz), pTheta(_pTheta), pDPhi(_pDPhi), pDy1(_pDy1), pDx1(_pDx1), pDx2(_pDx2), pAlp1(_pAlp1), pDy2(_pDy2), pDx3(_pDx3), pDx4(_pDx4), pAlp2(_pAlp2)
  {
    SetMesh(CSGMesh::ConstructTrap( pDz,  pTheta,  pDPhi,  pDy1,  pDx1,  pDx2,  pAlp1,  pDy2,  pDx3,  pDx4,  pAlp2));
  }
  const double pDz, pTheta, pDPhi, pDy1, pDx1, pDx2, pAlp1, pDy2, pDx3, pDx4, pAlp2;
};
#endif
