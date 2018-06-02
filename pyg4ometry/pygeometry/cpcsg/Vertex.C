#include "Vertex.h"

Vertex::Vertex(){
  pos = NULL;
  norm = NULL;
}

Vertex::Vertex(Vector* _pos){
  pos = _pos;
  norm = NULL;
}

Vertex::Vertex(Vector* _pos, Vector* _norm){
  pos = _pos;
  norm = _norm;
}

Vertex::~Vertex(){
  delete pos;
  delete norm;
}

Vector* Vertex::position(){
  return pos;
}

void Vertex::position(Vector* _pos){
  pos = _pos;
}

Vector* Vertex::normal(){
  return norm;
}

void Vertex::normal(Vector* _norm){
  norm = _norm;
}


Vertex::Vertex(const Vertex& rhs){
  pos = rhs.pos;
  norm = rhs.norm;
}

Vertex* Vertex::clone(){
  Vector* new_pos = new Vector(*pos);
  Vector* new_norm = NULL;
  if(norm)
  new_norm = new Vector(*norm);
  return new Vertex(new_pos,new_norm);
}

void Vertex::flip(){
  if(norm) norm->negated(); 
}

/*Vertex Vertex::interpolate(const Vertex& other, double t){
  return Vertex(pos->lerp(other.pos,t),norm->lerp(other.norm,t));
}*/

Vertex* Vertex::interpolate(Vertex* other, double t){
  Vector* new_pos = new Vector(pos->lerp(*other->pos,t));
  Vector* new_norm = NULL;
  if(norm && other->norm) new_norm = new Vector(norm->lerp(*other->norm,t)); 
  return new Vertex(new_pos,new_norm);
}
