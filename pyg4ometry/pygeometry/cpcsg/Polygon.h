#ifndef POLYGON_H
#define POLYGON_H
#include <vector>

#include "Vector.h"
#include "Vertex.h"

class Plane;

class Polygon{
  public:
    Polygon(const std::vector<Vertex*>& _vertices, void* _shared);
    ~Polygon();
    Polygon* clone();
    void flip();
    unsigned int size();
    Vertex* GetVertex(std::size_t i);
    std::vector<Vertex*> GetVertices();
    Plane* GetPlane();
    void SetPlane(Plane* _plane);
    void* GetShared();
  //private:
    std::vector<Vertex*> vertices;
    Plane* plane;
    void* shared;
};


#endif
