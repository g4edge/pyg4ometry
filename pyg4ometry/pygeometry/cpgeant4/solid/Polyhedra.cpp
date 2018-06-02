#include "Polyhedra.h"
#include "Polycone.h"
#include <cmath>

CSG* CSGMesh::ConstructPolyhedra(double phiStart, double phiTotal,int numSide,int numZPlanes,std::vector<double> zPlane,std::vector<double> rInner,std::vector<double> rOuter){
  double fillfrac = phiTotal/(2.0*M_PI);
  double slices = double(numSide)/fillfrac;
  Polycone* ph = new Polycone("polycone_temp",phiStart,phiTotal,zPlane,rInner,rOuter,int(ceil(slices)));
  return ph->GetMesh();
}
