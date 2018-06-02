#include "Tubs.h"

CSG* CSGMesh::ConstructTubs(double pRmin,double pRmax,double pDz,double pSPhi,double pDPhi){
  CSG* basicmesh = Solids::Cylinder(pDz,pRmax);

  if(pRmin == 0 && pSPhi == 0.0 && pDPhi == 2.0*M_PI){
    return basicmesh;
  }
  double wzlength = 3.0*pDz;
  double wrmax = 3.0*pRmax;

  CSG* pWedge;
  if(pDPhi == 2.0*M_PI){
    Wedge* wedge_temp = new Wedge("wedge_temp",wrmax,pSPhi,pSPhi+pDPhi-0.0001,wzlength);
    pWedge = wedge_temp->GetMesh();
  }
  else{
    Wedge* wedge_temp = new Wedge("wedge_temp",wrmax,pSPhi,pSPhi+pDPhi,wzlength);
    pWedge = wedge_temp->GetMesh();
  }
  CSG* mesh;
  if(pRmin != 0.0){
    CSG* sInner = Solids::Cylinder(pDz,pRmin);
    mesh = basicmesh->Subtract(sInner)->Subtract(pWedge->Inverse());
  }
  else{
    mesh = basicmesh->Subtract(pWedge->Inverse());
  }
  return mesh;
}
