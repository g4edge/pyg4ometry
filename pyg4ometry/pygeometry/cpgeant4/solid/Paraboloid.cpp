#include "Paraboloid.h"
#include <cmath>

void CSGMesh::ParaboloidAppendVertex(std::vector<Vertex*>& vertices,double theta,double z,double k1,double k2){
  double rho = 0.0;
  if(k1 != 0.0 && k2 != 0.0){
    rho = sqrt(k1*z+k2);
  }
  double x = rho*cos(theta);
  double y = rho*sin(theta);
  Vector* d = new Vector(x,y,z);
  vertices.push_back(new Vertex(d,d));
}

CSG* CSGMesh::ConstructParaboloid(double pDz,double pR1,double pR2,int stacks,int slices){
  double sz = -pDz;
  double dz = 2.0*pDz/double(stacks);
  double dTheta = (2.0*M_PI)/double(slices);

  double K1 = (pow(pR2,2.0)-pow(pR1,2.0))/(2.0*pDz);
  double K2 = (pow(pR2,2.0)+pow(pR1,2.0))/2.0;

  std::vector<Polygon*> polygons;
  for(int j0=0;j0 < stacks;j0++){
    double j1 = j0 + 0.5;
    double j2 = j0 + 1.0;
    for(int i0=0;i0<slices;i0++){
      double i1 = i0 + 0.5;
      double i2 = i0 + 1.0;
      std::vector<Vertex*> verticesN;
      CSGMesh::ParaboloidAppendVertex(verticesN, i1 * dTheta, j1 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesN, i2 * dTheta, j2 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesN, i0 * dTheta, j2 * dz + sz,K1,K2);
      polygons.push_back(new Polygon(verticesN,NULL));
      std::vector<Vertex*> verticesS;
      CSGMesh::ParaboloidAppendVertex(verticesS, i1 * dTheta, j1 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesS, i0 * dTheta, j0 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesS, i2 * dTheta, j0 * dz + sz,K1,K2);
      polygons.push_back(new Polygon(verticesS,NULL));
      std::vector<Vertex*> verticesW;
      CSGMesh::ParaboloidAppendVertex(verticesW, i1 * dTheta, j1 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesW, i0 * dTheta, j2 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesW, i0 * dTheta, j0 * dz + sz,K1,K2);
      polygons.push_back(new Polygon(verticesW,NULL));
      std::vector<Vertex*> verticesE;
      CSGMesh::ParaboloidAppendVertex(verticesE, i1 * dTheta, j1 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesE, i2 * dTheta, j0 * dz + sz,K1,K2);
      CSGMesh::ParaboloidAppendVertex(verticesE, i2 * dTheta, j2 * dz + sz,K1,K2);
      polygons.push_back(new Polygon(verticesE,NULL));
    }
  }
  for(int i0=0;i0<slices;i0++){
    double i1 = i0 + 1.0;
    std::vector<Vertex*> vertices1;
    CSGMesh::ParaboloidAppendVertex(vertices1, i0 * dTheta, sz,K1,K2);
    CSGMesh::ParaboloidAppendVertex(vertices1, 0, sz, 0,K2); //Setting K1=0 forces a zero vector which is used as the center
    CSGMesh::ParaboloidAppendVertex(vertices1, i1 * dTheta, sz,K1,K2);
    polygons.push_back(new Polygon(vertices1,NULL));

    std::vector<Vertex*> vertices2;
    CSGMesh::ParaboloidAppendVertex(vertices2, i1 * dTheta, stacks * dz + sz,K1,K2);
    CSGMesh::ParaboloidAppendVertex(vertices2, 0, stacks*dz + sz, 0,K2);
    CSGMesh::ParaboloidAppendVertex(vertices2, i0 * dTheta, stacks * dz + sz,K1,K2);
    polygons.push_back(new Polygon(vertices2,NULL));
  }
  return CSG::fromPolygons(polygons);
}
