#include "Sphere.h"
#include <vector>
#include <cmath>

void CSGMesh::SphereAppendVertex(std::vector<Vertex *>& vertices, double theta, double phi, double r) {
  if(r > 0){
    Vector d = Vector(cos(phi)*sin(theta),sin(phi)*sin(theta),cos(theta));
    vertices.push_back(new Vertex(new Vector(d.times(r)),NULL));
  }
  else{
    vertices.push_back(new Vertex(new Vector(0.0,0.0,0.0),NULL));
  }
}

CSG* CSGMesh::ConstructSphere(double pRmin,double pRmax,double pSPhi,double pDPhi,double pSTheta,double pDTheta,int nslice, int nstack){
  std::vector<Polygon*> polygons;

  double dTheta = pDTheta/double(nslice);
  double dPhi = pDPhi/double(nstack);

  int botPoleIn = ((pSPhi/M_PI)-floor(pSPhi/M_PI) == 0.0 ) ? 1 : 0;
  int topPoleIn = (pSPhi+pDPhi >= M_PI) ? 1 : 0;

  double r = pRmax;
  if(botPoleIn){
    for(int i0=0;i0<nslice;i0++){
      int i1 = i0 + 1;
      std::vector<Vertex*> vertices;
      CSGMesh::SphereAppendVertex(vertices,i0*dTheta+pSTheta,pSPhi,r);
      CSGMesh::SphereAppendVertex(vertices,i1*dTheta+pSTheta,dPhi+pSPhi,r);
      CSGMesh::SphereAppendVertex(vertices,i0*dTheta+pSTheta,dPhi+pSPhi,r);
      polygons.push_back(new Polygon(vertices,NULL));
    }
  }
  if(topPoleIn){
    int j0 = nstack - 1;
    int j1 = j0 + 1;
    for(int i0=0;i0<nslice;i0++){
      int i1 = i0 + 1;
      std::vector<Vertex*> vertices;
      CSGMesh::SphereAppendVertex(vertices,i0*dTheta+pSTheta,j0*dPhi+pSPhi,r);
      CSGMesh::SphereAppendVertex(vertices,i1*dTheta+pSTheta,j0*dPhi+pSPhi,r);
      CSGMesh::SphereAppendVertex(vertices,i0*dTheta+pSTheta,j1*dPhi+pSPhi,r);
      polygons.push_back(new Polygon(vertices,NULL));
    }
  }

  for(int j0=botPoleIn;j0<nstack-topPoleIn;j0++){
    double j1 = j0 + 0.5;
    double j2 = j0 + 1.0;
    for(int i0=0;i0<nslice;i0++){
      double i1 = i0 + 0.5;
      double i2 = i0 + 1.0;
      std::vector<Vertex*> verticesN;
      CSGMesh::SphereAppendVertex(verticesN, i1 * dTheta + pSTheta, j1 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesN, i2 * dTheta + pSTheta, j2 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesN, i0 * dTheta + pSTheta, j2 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(verticesN,NULL));
      std::vector<Vertex*> verticesS;
      CSGMesh::SphereAppendVertex(verticesS, i1 * dTheta + pSTheta, j1 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesS, i0 * dTheta + pSTheta, j0 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesS, i2 * dTheta + pSTheta, j0 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(verticesS,NULL));
      std::vector<Vertex*> verticesW;
      CSGMesh::SphereAppendVertex(verticesW, i1 * dTheta + pSTheta, j1 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesW, i0 * dTheta + pSTheta, j2 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesW, i0 * dTheta + pSTheta, j0 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(verticesW,NULL));
      std::vector<Vertex*> verticesE;
      CSGMesh::SphereAppendVertex(verticesE, i1 * dTheta + pSTheta, j1 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesE, i2 * dTheta + pSTheta, j0 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesE, i2 * dTheta + pSTheta, j2 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(verticesE,NULL));
    }
  }

  for(int i0=0;i0<nslice;i0++){
    int i1 = i0 + 1;
    std::vector<Vertex*> verticesNT;
    if(!topPoleIn){
      CSGMesh::SphereAppendVertex(verticesNT, i1 * dTheta + pSTheta, nstack * dPhi+pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesNT, 0.0, 0.0, 0.0);
      CSGMesh::SphereAppendVertex(verticesNT, i0 * dTheta + pSTheta, nstack * dPhi+pSPhi, r);
      polygons.push_back(new Polygon(verticesNT,NULL));
    }
    std::vector<Vertex*> verticesNB;
    if(!botPoleIn){
      CSGMesh::SphereAppendVertex(verticesNB, i0 * dTheta + pSTheta, pSPhi, r);
      CSGMesh::SphereAppendVertex(verticesNB, 0.0, 0.0, 0.0);
      CSGMesh::SphereAppendVertex(verticesNB, i1 * dTheta + pSTheta, pSPhi, r);
      polygons.push_back(new Polygon(verticesNB,NULL));
    }
  }

  if((pDTheta/(2.*M_PI))-floor(pDTheta/(2.*M_PI)) != 0.0){
    for(int j0=0;j0 < nstack;j0++){
      int j1 = j0 + 1;
      std::vector<Vertex*> vertices1;
      CSGMesh::SphereAppendVertex(vertices1, pSTheta, j1 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(vertices1, 0.0, 0.0, 0.0);
      CSGMesh::SphereAppendVertex(vertices1, pSTheta, j0 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(vertices1,NULL));

      std::vector<Vertex*> vertices2;
      CSGMesh::SphereAppendVertex(vertices2, nslice * dTheta + pSTheta, j0 * dPhi + pSPhi, r);
      CSGMesh::SphereAppendVertex(vertices2, 0., 0, 0.);
      CSGMesh::SphereAppendVertex(vertices2, nslice * dTheta + pSTheta, j1 * dPhi + pSPhi, r);
      polygons.push_back(new Polygon(vertices2,NULL));
    }
  }
  CSG* mesh = CSG::fromPolygons(polygons);
  if(pRmin > 0.0){
    CSG* mesh_inner = Solids::Sphere(pRmin,nslice,nstack);
    return mesh->Subtract(mesh_inner);
  }
  else{
    return mesh;
  }
}
