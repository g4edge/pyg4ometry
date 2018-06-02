#include "Polygon.h"
#include "Plane.h"

Polygon::Polygon(const std::vector<Vertex*>& _vertices, void* _shared){
  vertices = _vertices;
  shared = _shared;
  plane = Plane::fromPoints(vertices[0]->position(),vertices[1]->position(),vertices[2]->position());
}

Polygon::~Polygon(){
  for(int i=0;i<vertices.size();i++){
    delete vertices[i];
  }
  vertices.clear();
  delete plane;
}

unsigned int Polygon::size(){
  return vertices.size();
}

Vertex* Polygon::GetVertex(std::size_t i){
  return vertices[i];
}

std::vector<Vertex*> Polygon::GetVertices(){
  return vertices;
}

Plane* Polygon::GetPlane(){
  return plane;
}

void Polygon::SetPlane(Plane* _plane){
  plane = _plane;
}

void* Polygon::GetShared(){
  return shared;
}

Polygon* Polygon::clone(){
  std::vector<Vertex*> vclone;
  for(unsigned i = 0;i<vertices.size();i++){
    vclone.push_back(vertices[i]->clone());
  }
  return new Polygon(vclone,shared);
}

void Polygon::flip(){
  std::reverse(vertices.begin(),vertices.end()); 
  for(unsigned i = 0;i<vertices.size();i++){
    vertices[i]->flip();
  } 
  plane->flip();
}

