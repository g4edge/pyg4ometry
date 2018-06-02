#ifndef TET_H
#define TET_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Tet : public SolidBase{
public:
  Tet(std::string name,Vector* _anchor,Vector* _p2,Vector* _p3,Vector* _p4,bool _degeneracyFlag = false):
      SolidBase(name,"Tet"), degeneracyFlag(_degeneracyFlag)
  {
    anchor = _anchor;
    p2 = _p2;
    p3 = _p3;
    p4 = _p4;
    SetMesh(CSGMesh::ConstructTet(anchor,p2,p3,p4,degeneracyFlag));
  }
  Vector* anchor;
  Vector* p2;
  Vector* p3;
  Vector* p4;
  const bool degeneracyFlag;
};
#endif
