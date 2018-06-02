#include "Wedge.h"

CSG* CSGMesh::ConstructWedge(double pRMax,double pSPhi,double pDPhi,double halfzlength){
  double d = halfzlength;
  int nslice = 16;
  std::vector<double> x(nslice);
  std::vector<double> y(nslice);
  std::vector<Vertex*> p1(nslice);
  std::vector<Vertex*> p2(nslice);

  for(int i=0;i<nslice;i++){
    double phi = pSPhi + double(i)*(pDPhi-pSPhi)/double(nslice);
    x[i] = pRMax*cos(phi);
    y[i] = pRMax*sin(phi);
    p1[i] = new Vertex(new Vector(x[i],y[i],-d),NULL);
    p2[i] = new Vertex(new Vector(x[i],y[i], d),NULL);
  }

  std::vector<Polygon*> polygons;
  Vertex* vZero1 = new Vertex(new Vector(0.0,0.0,-d),NULL);
  Vertex* vZero2 = new Vertex(new Vector(0.0,0.0, d),NULL);

  for(int i=0;i<nslice-1;i++){
    //top triangle
    std::vector<Vertex*> vtx1(3);
    vtx1[0] = vZero2;vtx1[1] = p2[i];vtx1[2]=p2[i+1];
    polygons.push_back(new Polygon(vtx1,NULL));

    //bottom triangle
    std::vector<Vertex*> vtx2(3);
    vtx2[0] = vZero1;vtx2[1] = p1[i];vtx2[2]=p1[i+1];
    polygons.push_back(new Polygon(vtx2,NULL));

    //end square
    std::vector<Vertex*> vtx3(4);
    vtx3[0] = p1[i];vtx3[1] = p1[i+1];vtx3[2]=p2[i+1];vtx3[3]=p2[i];
    polygons.push_back(new Polygon(vtx3,NULL));
  }
  //first end face
  std::vector<Vertex*> vtxf(4);
  vtxf[0] = vZero1;vtxf[1] = p1[0];vtxf[2] = p2[0];vtxf[3] = vZero2;
  polygons.push_back(new Polygon(vtxf,NULL));

  std::vector<Vertex*> vtxe(4);
  vtxe[0] = vZero1;vtxe[1] = vZero2;vtxe[2] = p2.back();vtxe[3] = p1.back();
  polygons.push_back(new Polygon(vtxe,NULL));

  return CSG::fromPolygons(polygons);
   
}
