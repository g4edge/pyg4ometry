#include "Vertex.h"
#include <vector>

struct VertsAndPolys{
  std::vector<Vertex*> verts;
  std::vector<std::vector<unsigned> > polys;
  int count;
};

