#ifndef SUBTRACTION_H
#define SUBTRACTION_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class Subtraction : public SolidBase{
public:
  Subtraction(std::string name,SolidBase* _obj1,SolidBase* _obj2,Vector* _anglevec,Vector* _transvec):
      SolidBase(name,"Subtraction"),anglevec(_anglevec),transvec(_transvec) {
    obj1 = _obj1;
    obj2 = _obj2;
    SetMesh(CSGMesh::ConstructSubtraction(obj1->GetMesh(), obj2->GetMesh(), anglevec, transvec));
    if (!GetMesh()) {
      std::cout << "Null mesh " << obj1->GetName() << ":" << obj1->GetType() << " " << obj2->GetName() << ":"
                << obj2->GetType() << std::endl;
    }
  }
  SolidBase* obj1;
  SolidBase* obj2;
  Vector* anglevec;
  Vector* transvec;
};
#endif
