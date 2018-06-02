#include "Intersection.h"
#include "Transformation.h"

CSG* CSGMesh::ConstructIntersection(CSG* m1,CSG* mesh2,Vector* anglevec,Vector* transvec){
  std::pair<Vector,double> rot = tbxyz(anglevec);
  CSG* m2 = mesh2->clone();
  Vector* rotvec = new Vector(rot.first);
  m2->rotate(rotvec,rot.second);
  delete rotvec;
  m2->translate(transvec);

  CSG* mesh = m1->Intersect(m2);
  if(mesh->toPolygons().size() == 0){
    std::cout << "Intersection null mesh" << std::endl;
    return NULL;
  }
  delete m1;
  delete m2;

  return mesh;
}
