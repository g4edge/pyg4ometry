#include "TwistedBox.h"

CSG* CSGMesh::ConstructTwistedBox(double twistedangle, double pDx, double pDy, double pDz, int refine){
  std::vector<std::vector<double> > vert_crd_up(4,std::vector<double>(3));
  std::vector<std::vector<double> > vert_crd_dn(4,std::vector<double>(3));

  vert_crd_up[0][0] = -pDx; vert_crd_up[0][1] = -pDy; vert_crd_up[0][2] = pDz;
  vert_crd_up[1][0] = pDx; vert_crd_up[1][1] = -pDy; vert_crd_up[1][2] = pDz;
  vert_crd_up[2][0] = pDx; vert_crd_up[2][1] = pDy; vert_crd_up[2][2] = pDz;
  vert_crd_up[3][0] = -pDx; vert_crd_up[3][1] = pDy; vert_crd_up[3][2] = pDz;

  vert_crd_dn[0][0] = -pDx; vert_crd_dn[0][1] = -pDy; vert_crd_dn[0][2] = -pDz;
  vert_crd_dn[1][0] = -pDx; vert_crd_dn[1][1] = pDy; vert_crd_dn[1][2] = -pDz;
  vert_crd_dn[2][0] = pDx; vert_crd_dn[2][1] = pDy; vert_crd_dn[2][2] = -pDz;
  vert_crd_dn[3][0] = pDx; vert_crd_dn[3][1] = -pDy; vert_crd_dn[3][2] = -pDz;

  std::vector<std::vector<double> > vert_crd_rot(4);

  for(int i=0;i<4;i++){
    std::vector<double> vrot(3);
    vrot[0] = vert_crd_up[i][0]*cos(twistedangle) - vert_crd_up[i][1]*sin(twistedangle);
    vrot[1] = vert_crd_up[i][0]*sin(twistedangle) + vert_crd_up[i][1]*cos(twistedangle);
    vrot[2] = vert_crd_up[i][2];
    vert_crd_rot[i] = vrot;
  }

  std::vector<Vertex*> vert_up(4);
  std::vector<Vertex*> vert_dn(4);

  for(int i=0;i<4;i++){
    vert_up[i] = new Vertex(new Vector(vert_crd_rot[i][0],vert_crd_rot[i][1],vert_crd_rot[i][2]),NULL);
    vert_dn[i] = new Vertex(new Vector(vert_crd_dn[i][0],vert_crd_dn[i][1],vert_crd_dn[i][2]),NULL);
  } 

  std::vector<Polygon*> polygons(12);
  //There's almost definitely a less stupid way to do this
  std::vector<Vertex*> v0(3);
  v0[0] = vert_dn[0]; v0[1] = vert_dn[1]; v0[2] = vert_dn[2];
  polygons[0] = new Polygon(v0,NULL);

  std::vector<Vertex*> v1(3);
  v1[0] = vert_dn[2]; v1[1] = vert_dn[3]; v1[2] = vert_dn[0];
  polygons[1] = new Polygon(v1,NULL);
  
  std::vector<Vertex*> v2(3);
  v2[0] = vert_up[0]; v2[1] = vert_up[1]; v2[2] = vert_up[2];
  polygons[2] = new Polygon(v2,NULL);
  
  std::vector<Vertex*> v3(3);
  v3[0] = vert_up[2]; v3[1] = vert_up[3]; v3[2] = vert_up[0];
  polygons[3] = new Polygon(v3,NULL);
  
  std::vector<Vertex*> v4(3);
  v4[0] = vert_dn[0]; v4[1] = vert_dn[3]; v4[2] = vert_up[1];
  polygons[4] = new Polygon(v4,NULL);

  std::vector<Vertex*> v5(3);
  v5[0] = vert_dn[0]; v5[1] = vert_up[1]; v5[2] = vert_up[0];
  polygons[5] = new Polygon(v5,NULL);

  std::vector<Vertex*> v6(3);
  v6[0] = vert_dn[1]; v6[1] = vert_up[2]; v6[2] = vert_dn[2]; 
  polygons[6] = new Polygon(v6,NULL);

  std::vector<Vertex*> v7(3);
  v7[0] = vert_dn[1]; v7[1] = vert_up[3]; v7[2] = vert_up[2];
  polygons[7] = new Polygon(v7,NULL);

  std::vector<Vertex*> v8(3);
  v8[0] = vert_dn[0]; v8[1] = vert_up[0]; v8[2] = vert_up[3];
  polygons[8] = new Polygon(v8,NULL);

  std::vector<Vertex*> v9(3);
  v9[0] = vert_up[3]; v9[1] = vert_dn[1]; v9[2] = vert_dn[0];
  polygons[9] = new Polygon(v9,NULL);

  std::vector<Vertex*> v10(3);
  v10[0] = vert_dn[3]; v10[1] = vert_dn[2]; v10[2] = vert_up[2];
  polygons[10] = new Polygon(v10,NULL);

  std::vector<Vertex*> v11(3);
  v11[0] = vert_up[2]; v11[1] = vert_up[1]; v11[2] = vert_dn[3];
  polygons[11] = new Polygon(v11,NULL);

  CSG* mesh = CSG::fromPolygons(polygons);
  for(int i=0;i<refine;i++){
    mesh = mesh->refine();
  }
  return mesh;
}
