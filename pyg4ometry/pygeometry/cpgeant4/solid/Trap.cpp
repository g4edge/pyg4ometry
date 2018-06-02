#include "Trap.h"

CSG* CSGMesh::ConstructTrap(double pDz, double pTheta, double pDPhi, double pDy1, double pDx1, double pDx2, double pAlp1, double pDy2, double pDx3, double pDx4, double pAlp2){
  double hlZ = pDz;
  
  double X1 = pDx1;
  double X2 = pDx2;
  double Y1 = pDy1;

  double Y2 = pDy2;
  double X3 = pDx3;
  double X4 = pDx4;

  double dX = 2.0*sin(pTheta)*pDz;
  double dY = 2.0*sin(pDPhi)*pDz;

  std::vector<std::vector<double> > poly0(4,std::vector<double>(3));
  std::vector<std::vector<double> > poly1(4,std::vector<double>(3));

  poly0[0][0] = -X2; poly0[0][1] = -Y1; poly0[0][2] = -hlZ;
  poly0[1][0] = -X1; poly0[1][1] = Y1;  poly0[1][2] = -hlZ;
  poly0[2][0] = X1;  poly0[2][1] = Y1;  poly0[2][2] = -hlZ;
  poly0[3][0] = X2;  poly0[3][1] = -Y1; poly0[3][2] = -hlZ;

  poly1[0][0] = -X3; poly1[0][1] = -Y2; poly1[0][2] = hlZ;
  poly1[1][0] = -X4; poly1[1][1] = Y2;  poly1[1][2] = hlZ;
  poly1[2][0] = X4;  poly1[2][1] = Y2;  poly1[2][2] = hlZ;
  poly1[3][0] = X3;  poly1[3][1] = -Y2; poly1[3][2] = hlZ;

  double A0 = 0.0;
  double A1 = 0.0;

  for(int i0=0;i0<3;i0++){
    int i1 = i0 + 1;
    A0 += 0.5*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1]);
    A1 += 0.5*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1]);
  }
  double Xc0 = 0.0;
  double Yc0 = 0.0;
  double Xc1 = 0.0;
  double Yc1 = 0.0;

  for(int i0=0;i0<3;i0++){
    int i1 = i0 + 1;
    Xc0   += (1./(6.*A0))*(poly0[i0][0]+poly0[i1][0])*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1]);
    Yc0   += (1./(6.*A0))*(poly0[i0][1]+poly0[i1][1])*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1]);
    Xc1   += (1./(6.*A1))*(poly1[i0][0]+poly1[i1][0])*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1]);
    Yc1   += (1./(6.*A1))*(poly1[i0][1]+poly1[i1][1])*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1]);
  }
  std::vector<double> C0(3);
  std::vector<double> C1(3);

  C0[0] = Xc0; C0[1] = Yc0; C0[2] = 0.;
  C1[0] = Xc1; C1[1] = Yc1; C1[2] = 0.;

  //Center in X-Y plane
  for(int i=0;i<4;i++){
    for(int j=0;j<3;j++){
      poly0[i][j] = poly0[i][j]-C0[j];
      poly1[i][j] = poly1[i][j]-C1[j];
    }
  }

  //Slant faces
  for(int i=0;i<4;i++){
    std::vector<double> vert = poly0[i];
    double y = vert[1];
    double z = vert[2];
    double x = vert[0] + y*tan(pAlp1);
    poly0[i][0] = x;
    poly0[i][1] = y;
    poly0[i][2] = z;

    vert = poly1[i];
    y = vert[1];
    z = vert[2];
    x = vert[0] + y*tan(pAlp2);
    poly1[i][0] = x;
    poly1[i][1] = y;
    poly1[i][2] = z;
  }
  //Translate to original coordinates
  for(int i=0;i<4;i++){
    for(int j=0;j<3;j++){
      poly0[i][j] = poly0[i][j]+C0[j];
      poly1[i][j] = poly1[i][j]+C1[j];
    }
  }
  std::vector<double> dXY(3);
  dXY[0] = dX/2.; dXY[1] = dY/2.; dXY[2] = 0.;
  for(int i=0;i<4;i++){
    for(int j=0;j<3;j++){
      poly0[i][j] = poly0[i][j]-dXY[j];
      poly1[i][j] = poly1[i][j]+dXY[j];
    }
  }

  std::vector<Polygon*> polygons;

  //Top face
  std::vector<Vertex*> vtop;
  vtop.push_back(new Vertex(new Vector(poly1[3][0], poly1[3][1], poly1[3][2]),NULL));
  vtop.push_back(new Vertex(new Vector(poly1[2][0], poly1[2][1], poly1[2][2]),NULL));
  vtop.push_back(new Vertex(new Vector(poly1[1][0], poly1[1][1], poly1[1][2]),NULL));
  vtop.push_back(new Vertex(new Vector(poly1[0][0], poly1[0][1], poly1[0][2]),NULL));
  polygons.push_back(new Polygon(vtop,NULL));

  //Bottom face
  std::vector<Vertex*> vbot;
  vbot.push_back(new Vertex(new Vector(poly0[0][0], poly0[0][1], poly0[0][2]),NULL));
  vbot.push_back(new Vertex(new Vector(poly0[1][0], poly0[1][1], poly0[1][2]),NULL));
  vbot.push_back(new Vertex(new Vector(poly0[2][0], poly0[2][1], poly0[2][2]),NULL));
  vbot.push_back(new Vertex(new Vector(poly0[3][0], poly0[3][1], poly0[3][2]),NULL));
  polygons.push_back(new Polygon(vbot,NULL));

  //Side faces
  std::vector<Vertex*> vside;
  vside.push_back(new Vertex(new Vector(poly1[1][0], poly1[1][1], poly1[1][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[1][0], poly0[1][1], poly0[1][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[0][0], poly0[0][1], poly0[0][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[0][0], poly1[0][1], poly1[0][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[2][0], poly1[2][1], poly1[2][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[2][0], poly0[2][1], poly0[2][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[1][0], poly0[1][1], poly0[1][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[1][0], poly1[1][1], poly1[1][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[3][0], poly1[3][1], poly1[3][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[3][0], poly0[3][1], poly0[3][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[2][0], poly0[2][1], poly0[2][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[2][0], poly1[2][1], poly1[2][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[0][0], poly1[0][1], poly1[0][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[0][0], poly0[0][1], poly0[0][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly0[3][0], poly0[3][1], poly0[3][2]),NULL));
  vside.push_back(new Vertex(new Vector(poly1[3][0], poly1[3][1], poly1[3][2]),NULL));
  polygons.push_back(new Polygon(vside,NULL));

  return CSG::fromPolygons(polygons);
}
