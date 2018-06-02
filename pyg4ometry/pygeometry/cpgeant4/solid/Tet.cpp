#include "Tet.h"
#include <vector>

CSG* CSGMesh::ConstructTet(Vector* anchor,Vector* p2,Vector* p3,Vector* p4,bool degeneracyFlag){
  Vertex* vert_ancr = new Vertex(anchor,NULL);
  std::vector<Vertex*> vert_base(3);
  vert_base[0] = new Vertex(p2,NULL);
  vert_base[1] = new Vertex(p3,NULL);
  vert_base[2] = new Vertex(p4,NULL);

  std::vector<Polygon*> polygons(4);

  std::vector<Vertex*> vtx1(3);
  vtx1[0] = vert_base[2]; vtx1[1] = vert_base[1]; vtx1[2] = vert_base[0];
  polygons[0] = new Polygon(vtx1,NULL);

  std::vector<Vertex*> vtx2(3);
  vtx2[0] = vert_base[1]; vtx2[1] = vert_ancr; vtx2[2] = vert_base[0];
  polygons[1] = new Polygon(vtx2,NULL);

  std::vector<Vertex*> vtx3(3);
  vtx3[0] = vert_base[2]; vtx3[1] = vert_ancr; vtx3[2] = vert_base[1];
  polygons[2] = new Polygon(vtx3,NULL);

  std::vector<Vertex*> vtx4(3);
  vtx4[0] = vert_base[0]; vtx4[1] = vert_ancr; vtx4[2] = vert_base[2];
  polygons[3] = new Polygon(vtx4,NULL);

  return CSG::fromPolygons(polygons);
}
