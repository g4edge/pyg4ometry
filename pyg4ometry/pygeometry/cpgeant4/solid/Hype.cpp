#include "Hype.h"
#include "G4Plane.h"
#include <cmath>
#include <vector>

void CSGMesh::HypeAppendVertex(std::vector<Vertex *> &vertices, double theta, double z,double r, double stereo) {
  double x = sqrt(pow(r,2.0)+pow(tan(stereo)*z,2.0));
  double x_rot = cos(theta)*x;
  double y_rot = sin(theta)*x;
  vertices.push_back(new Vertex(new Vector(x_rot,y_rot,z),NULL));
}

CSG* CSGMesh::ConstructHype(double innerRadius,double outerRadius,double innerStereo,double outerStereo,double halfLenZ,int slices,int stacks){
  double dz = 2.0*(halfLenZ+1.E-6)/double(stacks);
  double sz = -halfLenZ-1.E-6;
  double dTheta = (2.0*M_PI)/double(slices);
  std::vector<double> rinout;
  if(innerRadius == 0.0){
    rinout.push_back(outerRadius);
  }
  else{
    rinout.push_back(innerRadius);
    rinout.push_back(outerRadius);
  }
  std::vector<double> stinout(2);
  stinout[0] = innerStereo;
  stinout[1] = outerStereo;


  std::vector<CSG*> meshinout;
  for(unsigned i = 0;i < rinout.size();i++){
    std::vector<Polygon*> polygons;
    for(int j0=0;j0 < stacks;j0++){
      double j1 = j0 + 0.5;
      double j2 = j0 + 1.0;
      for(int i0=0;i0<slices;i0++){
        double i1 = i0 + 0.5;
        double i2 = i0 + 1.0;
        std::vector<Vertex*> verticesN;
        CSGMesh::HypeAppendVertex(verticesN, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesN, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesN, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i]);
        polygons.push_back(new Polygon(verticesN,NULL));
        std::vector<Vertex*> verticesS;
        CSGMesh::HypeAppendVertex(verticesS, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesS, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesS, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i]);
        polygons.push_back(new Polygon(verticesS,NULL));
        std::vector<Vertex*> verticesW;
        CSGMesh::HypeAppendVertex(verticesW, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesW, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesW, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i]);
        polygons.push_back(new Polygon(verticesW,NULL));
        std::vector<Vertex*> verticesE;
        CSGMesh::HypeAppendVertex(verticesE, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesE, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i]);
        CSGMesh::HypeAppendVertex(verticesE, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i]);
        polygons.push_back(new Polygon(verticesE,NULL));
      }
    }
    meshinout.push_back(CSG::fromPolygons(polygons));
  }//end rinout.size loop

  for(unsigned i=0;i<meshinout.size();i++){
    double wzlength = 3.0*halfLenZ;
    Vector* topNorm = new Vector(0.0,0.0,1.0);
    Vector* botNorm = new Vector(0.0,0.0,-1.0);

    G4Plane* topcut_temp = new G4Plane("pTopCut",topNorm,halfLenZ,wzlength);
    G4Plane* botcut_temp = new G4Plane("pBottomCut",botNorm,-halfLenZ,wzlength);

    CSG* pTopCut = topcut_temp->GetMesh();
    CSG* pBottomCut = botcut_temp->GetMesh();
    meshinout[i] = meshinout[i]->Subtract(pTopCut)->Subtract(pBottomCut);
  }
  CSG* mesh;
  if(innerRadius != 0.0){
    mesh = meshinout[1]->Subtract(meshinout[0]);
  }
  else{
    mesh = meshinout[0];
  }
  return mesh;
}
