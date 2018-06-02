#include "Orb.h"

CSG* CSGMesh::ConstructOrb(double pRmax){
  return Solids::Sphere(pRmax);
}
