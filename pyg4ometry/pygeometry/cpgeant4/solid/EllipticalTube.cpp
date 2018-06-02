#include "EllipticalTube.h"
#include <cmath>

void CSGMesh::EllipticalTubeAppendVertex(std::vector<Vertex*> vertices,double theta,double z,double dx,double dy,Vector* norm){
  double x = dx*cos(theta);
  double y = dy*sin(theta);
  Vector* d = new Vector(x,y,z);
  Vector* n;
  if(!norm){
    n = d;
  }
  else{
    n = norm;
  }
  return vertices.push_back(new Vertex(d,n));
}

CSG* CSGMesh::ConstructEllipticalTube(double pDx,double pDy,double pDz,int slices,int stacks){
  double sz = -pDz;
  double dz = (2.0*pDz)/stacks;
  double dTheta = (2.0*M_PI)/slices;

  std::vector<Polygon*> polygons;
  for(int j0=0;j0<slices;j0++){
    double j1 = j0 + 0.5;
    double j2 = j0 + 1.0;
    for(int i0=0;i0<stacks;i0++){
      double i1 = i0 + 0.5;
      double i2 = i0 + 1.0;
      std::vector<Vertex*> verticesN;
      EllipticalTubeAppendVertex(verticesN, i1 * dTheta, j1 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesN, i2 * dTheta, j2 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesN, i0 * dTheta, j2 * dz + sz,pDx,pDy,NULL);
      polygons.push_back(new Polygon(verticesN,NULL));
      std::vector<Vertex*> verticesS;
      EllipticalTubeAppendVertex(verticesS, i1 * dTheta, j1 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesS, i0 * dTheta, j0 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesS, i2 * dTheta, j0 * dz + sz,pDx,pDy,NULL);
      polygons.push_back(new Polygon(verticesS,NULL));
      std::vector<Vertex*> verticesW;
      EllipticalTubeAppendVertex(verticesW, i1 * dTheta, j1 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesW, i0 * dTheta, j2 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesW, i0 * dTheta, j0 * dz + sz,pDx,pDy,NULL);
      polygons.push_back(new Polygon(verticesW,NULL));
      std::vector<Vertex*> verticesE;
      EllipticalTubeAppendVertex(verticesE, i1 * dTheta, j1 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesE, i2 * dTheta, j0 * dz + sz,pDx,pDy,NULL);
      EllipticalTubeAppendVertex(verticesE, i2 * dTheta, j2 * dz + sz,pDx,pDy,NULL);
      polygons.push_back(new Polygon(verticesE,NULL));

    }
  }

  for(int i0=0;i0<slices;i0++){
    double i1 = i0 + 1;
    std::vector<Vertex*> vertices1;
    EllipticalTubeAppendVertex(vertices1,i0*dTheta,sz,pDz,pDy,new Vector(0.0,0.0,1.0));
    EllipticalTubeAppendVertex(vertices1,0,sz,0,0,new Vector(0.0,0.0,1.0));
    EllipticalTubeAppendVertex(vertices1,i1*dTheta,sz,pDz,pDy,new Vector(0.0,0.0,1.0));
    polygons.push_back(new Polygon(vertices1,NULL));

    std::vector<Vertex*> vertices2;
    EllipticalTubeAppendVertex(vertices2,i1*dTheta,stacks*dz+sz,pDx,pDy,new Vector(0.0,0.0,-1.0));
    EllipticalTubeAppendVertex(vertices2,0,stacks*dz+sz,0,0,new Vector(0.0,0.0,-1.0));
    EllipticalTubeAppendVertex(vertices2,i0*dTheta,stacks*dz+sz,pDx,pDy,new Vector(0.0,0.0,-1.0));
    polygons.push_back(new Polygon(vertices2,NULL));
  }

  return CSG::fromPolygons(polygons);
}
