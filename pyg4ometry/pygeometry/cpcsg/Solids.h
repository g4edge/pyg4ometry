#ifndef __SOLIDS__
#define __SOLIDS__
#include "CSG.h"
#include "Polygon.h"
#include "Vertex.h"
#include "Vector.h"

class Solids {
  public:
  static CSG* Box(double dx,double dy,double dz);
  static CSG* Sphere(double r,int slices = 16,int stacks = 8);
  static CSG* Cylinder(double dz,double r,int slices = 16); 
  static CSG* Cone(double dz,double r,int slices = 16);
  static CSG* Cone(Vector* start,Vector* end,double r,int slices = 16);
};
#endif
