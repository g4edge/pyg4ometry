#include "Para.h"
#include <cmath>

CSG* CSGMesh::ConstructPara(double pX,double pY,double pZ,double pAlpha,double pTheta,double pPhi){
  double dx_y = pY*sin(pAlpha);
  double dx_z = pZ*sin(pTheta);
  double dy = pZ*sin(pPhi);
  double dz = pZ-pZ*cos(pPhi);

  std::vector<Polygon*> polygons(6);

  std::vector<Vertex*> vtx1(4);
  vtx1[0] = new Vertex(new Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  vtx1[1] = new Vertex(new Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  vtx1[2] = new Vertex(new Vector( pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  vtx1[3] = new Vertex(new Vector( pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  polygons[0] = new Polygon(vtx1,NULL);

  std::vector<Vertex*> vtx2(4);
  vtx2[0] = new Vertex(new Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  vtx2[1] = new Vertex(new Vector( pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  vtx2[2] = new Vertex(new Vector( pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  vtx2[3] = new Vertex(new Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  polygons[1] = new Polygon(vtx2,NULL);

  std::vector<Vertex*> vtx3(4);
  vtx3[0] = new Vertex(new Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  vtx3[1] = new Vertex(new Vector( pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  vtx3[2] = new Vertex(new Vector( pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  vtx3[3] = new Vertex(new Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  polygons[2] = new Polygon(vtx3,NULL);

  std::vector<Vertex*> vtx4(4);
  vtx4[0] = new Vertex(new Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  vtx4[1] = new Vertex(new Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  vtx4[2] = new Vertex(new Vector( pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  vtx4[3] = new Vertex(new Vector( pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  polygons[3] = new Polygon(vtx4,NULL);

  std::vector<Vertex*> vtx5(4);
  vtx5[0] = new Vertex(new Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  vtx5[1] = new Vertex(new Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  vtx5[2] = new Vertex(new Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  vtx5[3] = new Vertex(new Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  polygons[4] = new Polygon(vtx5,NULL);

  std::vector<Vertex*> vtx6(4);
  vtx6[0] = new Vertex(new Vector( pX-dx_y-dx_z,-pY-dy,-pZ+dz), NULL);
  vtx6[1] = new Vertex(new Vector( pX+dx_y-dx_z, pY-dy,-pZ+dz), NULL);
  vtx6[2] = new Vertex(new Vector( pX+dx_y+dx_z, pY+dy, pZ-dz), NULL);
  vtx6[3] = new Vertex(new Vector( pX-dx_y+dx_z,-pY+dy, pZ-dz), NULL);
  polygons[5] = new Polygon(vtx6,NULL);
  return CSG::fromPolygons(polygons);
}
