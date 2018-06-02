#ifndef OPTICALSURFACE_H
#define OPTICALSURFACE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"

class OpticalSurface : public SolidBase{
public:
  OpticalSurface(std::string name,std::string _finish,std::string _model,std::string _value):
      SolidBase(name,"OpticalSurface"),finish(_finish),model(_model),value(_value)
  {
  }
  std::string finish,model,value;
};
#endif //CPGEANT4_OPTICALSURFACE_H
