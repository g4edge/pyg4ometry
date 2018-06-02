#ifndef PLANE_H
#define PLANE_H
#include <vector>
#include "Vector.h"
#include "Vertex.h"

class Polygon;

class Plane {
 public:
  const double EPSILON= 1.e-5;
  Plane(Vector* _normal, double _w);
  Plane(const Plane& plane); 
  ~Plane();
  Plane* clone();
  static Plane* fromPoints(const Vector* a, const Vector* b, const Vector* c);
  void flip(); 
  void splitPolygon(Polygon* polygon, 
		    std::vector<Polygon*> &coplanarFront, 
		    std::vector<Polygon*> &coplanarBack,
		    std::vector<Polygon*> &front,
		    std::vector<Polygon*> &back);
  Vector* normal();
  double par();
 private:
  Vector* norm;
  double w;
  enum PolyType {INIT = -1,COPLANAR=0,FRONT,BACK,SPANNING};
};

#endif
