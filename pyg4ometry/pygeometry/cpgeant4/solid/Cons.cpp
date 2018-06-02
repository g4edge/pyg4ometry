#include "Cons.h"

CSG* CSGMesh::ConstructCons(double pRmin1,double pRmax1,double pRmin2,double pRmax2,double pDz,double pSPhi,double pDPhi){
  double R1,r1,R2,r2;
  double factor;
  if(pRmax1 < pRmax2){
    R1 = pRmax2;
    r1 = pRmin2;
    R2 = pRmax1;
    r2 = pRmin1;
    factor = -1.0;
  }
  else{
    R1 = pRmax1;
    r1 = pRmin1;
    R2 = pRmax2;
    r2 = pRmin2;
    factor = 1.0;
  }
  double h = 2.0*pDz; 
  double H1 = (R2*h)/(R1-R2);
  double H2 = 0.;
  if(r1-r2 != 0.0){
    H2 = (r2*h)/(r1-r2);
  }

  double h1 = factor*(h+H1);
  double h2 = factor*(h+H2);

  CSG* basicmesh = Solids::Cone(new Vector(0.0,0.0,-factor*pDz),new Vector(0.0,0.0,h1-factor),R1);


  double wrmax = 3.0*(pRmax1+pRmax2); // ensure radius for intersection wedge is much bigger than solid
  double wzlength = 3.0*pDz;

  CSG* pWedge; 
  if( pDPhi != 2.0*M_PI ){
    SolidBase* wedge = new Wedge("wedge_temp",wrmax,pSPhi,pSPhi+pDPhi,wzlength);
    pWedge = wedge->GetMesh();
  }
  else{
    pWedge = Solids::Cylinder(5.*pDz,5.*R1);
  }

  G4Plane* TopCutPlane = new G4Plane("pTopCut_temp",new Vector(0.0,0.0,1.0),pDz,wzlength);
  CSG* pTopCut = TopCutPlane->GetMesh();

  G4Plane* BotCutPlane = new G4Plane("pBotCut_temp",new Vector(0.0,0.0,-1.0),-pDz,wzlength);
  CSG* pBotCut = BotCutPlane->GetMesh();

  CSG* mesh;
  if(H2 != 0.){
    CSG* sInner = Solids::Cone(new Vector(0.,0.,-factor*pDz),new Vector(0.0,0.0,h2-factor*pDz),r1);
    mesh = basicmesh->Subtract(sInner)->Intersect(pWedge)->Subtract(pBotCut)->Subtract(pTopCut);
  }
  else{
    mesh = basicmesh->Intersect(pWedge)->Subtract(pBotCut)->Subtract(pTopCut); 
  }
  return mesh;
}
