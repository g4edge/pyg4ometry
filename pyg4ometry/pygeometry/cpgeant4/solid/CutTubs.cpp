#include "CutTubs.h"

CSG* CSGMesh::ConstructCutTubs(double pRmin,double pRmax,double pDz,double pSPhi,double pDPhi,Vector* pLowNorm,Vector* pHighNorm){
  Tubs* basictubs = new Tubs("tubs_temp",pRmin,pRmax,pDz,pSPhi,pDPhi);
  CSG* basicmesh = basictubs->GetMesh();
  if((pLowNorm->x() != 0.0 || pLowNorm->y() != 0.0 || pLowNorm->z() != -1.0)
      || (pHighNorm->x() != 0.0 || pHighNorm->y() != 0.0 || pHighNorm->z() != 1.0)){
    CSG* mesh;
    double zlength = 3.0*pDz; //make the dimensions of the semi-infinite plane large enough

    if(pHighNorm->x() != 0.0 || pHighNorm->y() != 0.0 || pHighNorm->z() != 1.0){
      G4Plane* pHigh_temp = new G4Plane("pHigh_temp",pHighNorm,pDz,zlength);
      CSG* pHigh = pHigh_temp->GetMesh();
      mesh = basicmesh->Subtract(pHigh);
    }
    if(pLowNorm->x() != 0.0 || pLowNorm->y() != 0.0 || pLowNorm->z() != -1.0){
      G4Plane* pLow_temp = new G4Plane("pLow_temp",pLowNorm,-pDz,zlength);
      CSG* pLow = pLow_temp->GetMesh();
      mesh = basicmesh->Subtract(pLow);
    }
    return mesh;
  }
  else{
    return basicmesh;
  } 
}
