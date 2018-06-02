#include "Polycone.h"
#include "Wedge.h"
#include <cmath>

void CSGMesh::PolyconeAppendVertex(std::vector<Vertex*>& vertices,double theta,double z,double r){
  double x = r*cos(theta);
  double y = r*sin(theta);
  vertices.push_back(new Vertex(new Vector(x,y,z),NULL));
}

CSG* CSGMesh::ConstructPolycone(double pSPhi,double pDPhi,std::vector<double> pZpl,std::vector<double> pRMin,std::vector<double> pRMax,int slices){
  double dPhi = (2.*M_PI)/double(slices);
  int stacks = pZpl.size();

  std::vector<std::vector<double> > rinout(2);
  rinout[0] = pRMin; rinout[1] = pRMax;

  std::vector<Polygon*> polygons;

  double offs = 1.E-25;
  for(int R = 0;R < 2;R++){
    for(int j0 = 0;j0 < stacks-1;j0++){
      double j1 = j0 + 0.5;
      double j2 = j0 + 1.0;
      double r0 = rinout[R][j0] + offs;
      double r2 = rinout[R][j2] + offs;
      for(int i0=0;i0 < slices;i0++){
        double i1 = i0 + 0.5;
        double i2 = i0 + 1.0;
        double k0 = (R == 1) ? i0 : i2;
        double k1 = (R == 1) ? i2 : i0;
        std::vector<Vertex*> vertices;
        CSGMesh::PolyconeAppendVertex(vertices, k0 * dPhi + pSPhi, pZpl[j0], r0);
        CSGMesh::PolyconeAppendVertex(vertices, k1 * dPhi + pSPhi, pZpl[j0], r0);
        CSGMesh::PolyconeAppendVertex(vertices, k1 * dPhi + pSPhi, pZpl[j2], r2);
        CSGMesh::PolyconeAppendVertex(vertices, k0 * dPhi + pSPhi, pZpl[j2], r2);
        polygons.push_back(new Polygon(vertices,NULL));
      }
    }
  }

  for(int i0=0;i0 < slices;i0++){
    double i1 = i0 + 0.5;
    double i2 = i0 + 1.0;
    std::vector<Vertex*> vertices_t;
    std::vector<Vertex*> vertices_b;

    CSGMesh::PolyconeAppendVertex(vertices_t, i2 * dPhi + pSPhi, pZpl.back(), pRMin.back()+offs);
    CSGMesh::PolyconeAppendVertex(vertices_t, i0 * dPhi + pSPhi, pZpl.back(), pRMin.back()+offs);
    CSGMesh::PolyconeAppendVertex(vertices_t, i0 * dPhi + pSPhi, pZpl.back(), pRMax.back()+offs);
    CSGMesh::PolyconeAppendVertex(vertices_t, i2 * dPhi + pSPhi, pZpl.back(), pRMax.back()+offs);
    polygons.push_back(new Polygon(vertices_t,NULL));

    CSGMesh::PolyconeAppendVertex(vertices_b, i0 * dPhi + pSPhi, pZpl[0], pRMin[0]+offs);
    CSGMesh::PolyconeAppendVertex(vertices_b, i2 * dPhi + pSPhi, pZpl[0], pRMin[0]+offs);
    CSGMesh::PolyconeAppendVertex(vertices_b, i2 * dPhi + pSPhi, pZpl[0], pRMax[0]+offs);
    CSGMesh::PolyconeAppendVertex(vertices_b, i0 * dPhi + pSPhi, pZpl[0], pRMax[0]+offs);
    polygons.push_back(new Polygon(vertices_b,NULL));

  }
  CSG* mesh = CSG::fromPolygons(polygons);

  double wrmax = 0.0;
  double wzlength = 0.0;
  for(unsigned i=0;i<pZpl.size();i++){
    if(pRMax[i] > wrmax){
      wrmax = pRMax[i];
    }
    if(pZpl[i] > wzlength){
      wzlength = pZpl[i];
    }
  }
  wrmax *= 3.0;
  wzlength *= 3.0;

  if(pDPhi != 2.*M_PI){
    Wedge* wedge_temp = new Wedge("wedge_temp",wrmax,pSPhi,pDPhi+pSPhi,wzlength);
    CSG* pWedge = wedge_temp->GetMesh();
    mesh = pWedge->Intersect(mesh);
  }
  return mesh;

}
