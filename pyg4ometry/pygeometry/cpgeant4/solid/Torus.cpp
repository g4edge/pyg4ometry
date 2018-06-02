#include "Torus.h"
#include "Wedge.h"
#include <cmath>

void CSGMesh::TorusAppendVertex(std::vector<Vertex *> &vertices, double theta, double phi, double r,double pRtor) {
  double x = r*cos(theta)+pRtor;
  double z = r*sin(theta);
  double x_rot = cos(phi)*x;
  double y_rot = sin(phi)*x;
  vertices.push_back(new Vertex(new Vector(x_rot,y_rot,z)));
}

CSG* CSGMesh::ConstructTorus(double pRmin,double  pRmax,double  pRtor,double  sphi,double  pDPhi,int slices,int stacks){
  double dTheta = (2.0*M_PI)/double(stacks);
  double dPhi = (2.0*M_PI)/double(slices);

  std::vector<double> rinout(2);
  rinout[0] = pRmin;
  rinout[1] = pRmax;

  std::vector<CSG*> meshinout(2);

  for(int r=0;r<2;r++) {
    std::vector<Polygon*> polygons;
    for(int j0 = 0;j0 < slices;j0++){
      double j1 = j0 + 0.5;
      double j2 = j0 + 1.0;
      for(int i0 = 0;i0 < stacks; i0++){
        double i1 = i0 + 0.5;
        double i2 = i0 + 1.0;
        std::vector<Vertex*> verticesN;
        CSGMesh::TorusAppendVertex(verticesN, i1 * dTheta, j1 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesN, i2 * dTheta, j2 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesN, i0 * dTheta, j2 * dPhi + sphi, r,pRtor);
        polygons.push_back(new Polygon(verticesN,NULL));

        std::vector<Vertex*> verticesS;
        CSGMesh::TorusAppendVertex(verticesS, i1 * dTheta, j1 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesS, i0 * dTheta, j0 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesS, i2 * dTheta, j0 * dPhi + sphi, r,pRtor);
        polygons.push_back(new Polygon(verticesS,NULL));

        std::vector<Vertex*> verticesW;
        CSGMesh::TorusAppendVertex(verticesW, i1 * dTheta, j1 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesW, i0 * dTheta, j2 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesW, i0 * dTheta, j0 * dPhi + sphi, r,pRtor);
        polygons.push_back(new Polygon(verticesW,NULL));

        std::vector<Vertex*> verticesE;
        CSGMesh::TorusAppendVertex(verticesE, i1 * dTheta, j1 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesE, i2 * dTheta, j0 * dPhi + sphi, r,pRtor);
        CSGMesh::TorusAppendVertex(verticesE, i2 * dTheta, j2 * dPhi + sphi, r,pRtor);
        polygons.push_back(new Polygon(verticesE,NULL));
      }
    }
    meshinout[r] = CSG::fromPolygons(polygons);
  }//end of loop over

  CSG* mesh;
  if(pRmin != 0.){
    mesh = meshinout[0]->Subtract(meshinout[1]);
  }
  else{
    mesh = meshinout[1]->Inverse();
  }
  if(pDPhi != 2.0*M_PI){
    double wrmax = 3.0*pRtor;
    double wzlength = 5.0*pRmax;
    Wedge* wedge_temp = new Wedge("wedge_temp",wrmax,sphi,pDPhi,wzlength);
    CSG* pWedge = wedge_temp->GetMesh();
    mesh = pWedge->Intersect(mesh);
  }
  return mesh;
}
