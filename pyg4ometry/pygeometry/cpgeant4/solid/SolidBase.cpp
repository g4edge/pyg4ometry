#include "SolidBase.h"

SolidBase::SolidBase(std::string _name,std::string _type):name(_name),type(_type){

}

SolidBase::~SolidBase(){
  delete mesh;
}

void SolidBase::SetMesh(CSG* _mesh){
  mesh = _mesh;
}

CSG* SolidBase::GetMesh(){
  return mesh;
}

std::string SolidBase::GetName(){
  return name;
}

std::string SolidBase::GetType() {
  return type;
}