#include "EllipticalCone.h"
#include <cmath>

void CSGMesh::EllipticalConeAppendVertex(std::vector<Vertex*> vertices,double theta,double z,double dx,double dy,Vector* norm,double zMax){
  double x = dx*(((zMax-z)/zMax)*cos(theta));
  double y = dy*(((zMax-z)/zMax)*sin(theta));
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

CSG* CSGMesh::ConstructEllipticalCone(double pxSemiAxis,double pySemiAxis,double zMax,double pzTopCut,int slices,int stacks){
  double sz = -zMax/2.0;
  double dz = zMax/double(stacks);
  double dTheta = (2.*M_PI)/double(slices);

  double dxabs = pxSemiAxis*zMax;
  double dyabs = pySemiAxis*zMax;

  std::vector<Polygon*> polygons;

  for(int j0=0;j0 < slices;j0++){
    double j1 = j0 + 0.5;
    double j2 = j0 + 1.0;
    for(int i0=0;i0 < stacks;i0++){
      double i1 = i0 + 0.5;
      double i2 = i0 + 1.0;
      std::vector<Vertex*> verticesN;
      CSGMesh::EllipticalConeAppendVertex(verticesN, i1 * dTheta, j1 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesN, i2 * dTheta, j2 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesN, i0 * dTheta, j2 * dz + sz,dxabs,dyabs,NULL,zMax);
      polygons.push_back(new Polygon(verticesN,NULL));
      std::vector<Vertex*> verticesS;
      CSGMesh::EllipticalConeAppendVertex(verticesS, i1 * dTheta, j1 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesS, i0 * dTheta, j0 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesS, i2 * dTheta, j0 * dz + sz,dxabs,dyabs,NULL,zMax);
      polygons.push_back(new Polygon(verticesS,NULL));
      std::vector<Vertex*> verticesW;
      CSGMesh::EllipticalConeAppendVertex(verticesW, i1 * dTheta, j1 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesW, i0 * dTheta, j2 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesW, i0 * dTheta, j0 * dz + sz,dxabs,dyabs,NULL,zMax);
      polygons.push_back(new Polygon(verticesW,NULL));
      std::vector<Vertex*> verticesE;
      CSGMesh::EllipticalConeAppendVertex(verticesE, i1 * dTheta, j1 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesE, i2 * dTheta, j0 * dz + sz,dxabs,dyabs,NULL,zMax);
      CSGMesh::EllipticalConeAppendVertex(verticesE, i2 * dTheta, j2 * dz + sz,dxabs,dyabs,NULL,zMax);
      polygons.push_back(new Polygon(verticesE,NULL));
    }
  }

  for(int i0=0;i0 < slices;i0++){
    double i1 = i0 + 1.0;
    std::vector<Vertex*> vertices1;
    CSGMesh::EllipticalConeAppendVertex(vertices1, i0 * dTheta, sz,dxabs,dyabs, new Vector(0.,0.,1.),zMax);
    CSGMesh::EllipticalConeAppendVertex(vertices1, 0, sz,0,0,new Vector(0.0,0.0,1.0),zMax );
    CSGMesh::EllipticalConeAppendVertex(vertices1, i1 * dTheta, sz, dxabs,dyabs,new Vector(0.0,0.0,1.0),zMax);
    polygons.push_back(new Polygon(vertices1,NULL));


    std::vector<Vertex*> vertices2;
    CSGMesh::EllipticalConeAppendVertex(vertices2, i1 * dTheta, stacks * dz + sz,dxabs,dyabs,new Vector(0.0,0.0,-1.0),zMax);
    CSGMesh::EllipticalConeAppendVertex(vertices2, 0, slices*dz + sz,0,0,new Vector(0.0,0.0,-1.0),zMax);
    CSGMesh::EllipticalConeAppendVertex(vertices2, i0 * dTheta, stacks * dz + sz,dxabs,dyabs,new Vector(0.0,0.0,-1.0),zMax);
    polygons.push_back(new Polygon(vertices2,NULL));
  }

  return CSG::fromPolygons(polygons);
}
