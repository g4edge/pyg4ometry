#ifndef VERTEX_H
#define VERTEX_H

#include "Vector.h"

class Vertex {
 public:
  Vertex();
  Vertex(Vector* _pos);
  Vertex(Vector* _pos, Vector* _norm);
  Vertex(const Vertex& rhs);
  ~Vertex();
  
  Vertex* clone();
  void flip();
  //Vertex interpolate(const Vertex& other, double t); 
  Vertex* interpolate(Vertex* other, double t); 
  Vector* position();
  void position(Vector* _pos);
  Vector* normal();
  void normal(Vector* _norm);
 private:
  Vector* pos;
  Vector* norm;
};

#endif
