#ifndef CSG_MESH_H
#define CSG_MESH_H
#include "CSG.h"
#include "Vector.h"

struct ZSection;

namespace CSGMesh{
  CSG* ConstructBox(double px,double py,double pz);
  CSG* ConstructCons(double pRmin1, double pRmax1, double pRmin2,double pRmax2, double pDz, double pSPhi, double pDPhi);
  CSG* ConstructWedge(double pRMax,double pSPhi,double pDPhi,double halfzlength);
  CSG* ConstructPlane(Vector* normal,double dist,double zlength);
  CSG* ConstructTubs(double pRmin,double pRmax,double pDz,double pSPhi,double pDPhi);
  CSG* ConstructCutTubs(double pRmin,double pRmax,double pDz,double pSPhi,double pDPhi,Vector* pLowNorm,Vector* pHighNorm);
  CSG* ConstructTrap(double pDz, double pTheta, double pDPhi, double pDy1, double pDx1, double pDx2, double pAlp1, double pDy2, double pDx3, double pDx4, double pAlp2);
  CSG* ConstructTwistedBox(double twistedangle, double pDx, double pDy, double pDz, int refine);
  CSG* ConstructExtrudedSolid(std::vector<Vector*> pPolygon,std::vector<ZSection> pZslices);
  CSG* ConstructSphere(double pRmin,double pRmax,double pSPhi,double pDPhi,double pSTheta,double pDTheta,int nslice, int nstack);
  void SphereAppendVertex(std::vector<Vertex*>& vertices,double theta,double phi,double r);
  CSG* ConstructTet(Vector* anchor,Vector* p2,Vector* p3,Vector* p4,bool degeneracyFlag);
  CSG* ConstructTorus(double pRmin,double  pRmax,double  pRtor,double  pSPhi,double  pDPhi,int nslice,int nstack);
  void TorusAppendVertex(std::vector<Vertex*>& vertices,double theta,double phi,double r,double pRtor);
  CSG* ConstructTrd(double x1,double x2,double y1,double y2,double z);
  CSG* ConstructEllipsoid(double pxSemiAxis,double pySemiAxis,double pzSemiAxis,double pzBottomCut,double pzTopCut,int nslice,int nstack);
  void EllipsoidAppendVertex(std::vector<Vertex*>& vertices,double pxSemiAxis,double pySemiAxis,double pzSemiAxis,double u,double v);
  CSG* ConstructHype(double innerRadius,double outerRadius,double innerStereo,double outerStereo,double halfLenZ,int nslice,int nstack);
  void HypeAppendVertex(std::vector<Vertex*>& vertices,double theta,double z,double r,double stereo);
  CSG* ConstructOrb(double pRmax);
  CSG* ConstructPara(double pDx,double pDy,double pDz,double pAlpha,double pTheta,double pPhi);
  CSG* ConstructParaboloid(double pDz,double pR1,double pR2,int nstack,int nslice);
  void ParaboloidAppendVertex(std::vector<Vertex*>& vertices,double theta,double z,double k1,double k2);
  CSG* ConstructPolycone(double pSPhi,double pDPhi,std::vector<double> pZpl,std::vector<double> pRMin,std::vector<double> pRMax,int nslice);
  void PolyconeAppendVertex(std::vector<Vertex*>& vertices,double theta,double z,double r);
  CSG* ConstructPolyhedra(double phiStart, double phiTotal,int numSide,int numZPlanes,std::vector<double> zPlane,std::vector<double> rInner,std::vector<double> rOuter);
  CSG* ConstructEllipticalCone(double pxSemiAxis,double pySemiAxis,double zMax,double pzTopCut,int nslice,int nstack);
  void EllipticalConeAppendVertex(std::vector<Vertex*> vertices,double theta,double z,double dx,double dy,Vector* norm,double zMax);
  CSG* ConstructEllipticalTube(double pDx,double pDy,double pDz,int nslice,int nstack);
  void EllipticalTubeAppendVertex(std::vector<Vertex*> vertices,double theta,double z,double dx,double dy,Vector* norm);

  CSG* ConstructUnion(CSG* mesh1,CSG* mesh2,Vector* anglevec,Vector* transvec);
  CSG* ConstructSubtraction(CSG* mesh1,CSG* mesh2,Vector* anglevec,Vector* transvec);
  CSG* ConstructIntersection(CSG* mesh1,CSG* mesh2,Vector* anglevec,Vector* transvec);
};

struct ZSection{
  ZSection(double _z,Vector* _offset,double _scale):
      z(_z),offset(_offset),scale(_scale) {}
  double z;
  Vector* offset;
  double scale;
};
#endif