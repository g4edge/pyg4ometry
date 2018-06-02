#include "Ellipsoid.h"
#include "G4Plane.h"

void CSGMesh::EllipsoidAppendVertex(std::vector<Vertex*>& vertices,double pxSemiAxis,double pySemiAxis,double pzSemiAxis,double u,double v){
  vertices.push_back(new Vertex(new Vector(pxSemiAxis*cos(u)*sin(v),pySemiAxis*cos(u)*cos(v),pzSemiAxis*sin(u)),NULL));
}

CSG* CSGMesh::ConstructEllipsoid(double pxSemiAxis,double pySemiAxis,double pzSemiAxis,double pzBottomCut,double pzTopCut,int slices,int stacks){
  std::vector<Polygon*> polygons;
  double du = M_PI/double(slices);
  double dv = (2.0*M_PI)/double(stacks);

  double su = -M_PI/2.0;
  double sv = -M_PI;

  for(int j0=0;j0 < slices;j0++){
    double j1 = j0 + 0.5;
    double j2 = j0 + 1.0;
    for(int i0=0;i0 < stacks;i0++){
      double i1 = i0 + 0.5;
      double i2 = i0 + 1.0;

      std::vector<Vertex*> verticesN;
      CSGMesh::EllipsoidAppendVertex(verticesN,pxSemiAxis,pySemiAxis,pzSemiAxis, i1 * du + su, j1 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesN,pxSemiAxis,pySemiAxis,pzSemiAxis, i2 * du + su, j2 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesN,pxSemiAxis,pySemiAxis,pzSemiAxis, i0 * du + su, j2 * dv + sv);
      polygons.push_back(new Polygon(verticesN,NULL));

      std::vector<Vertex*> verticesS;
      CSGMesh::EllipsoidAppendVertex(verticesS,pxSemiAxis,pySemiAxis,pzSemiAxis, i1 * du + su, j1 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesS,pxSemiAxis,pySemiAxis,pzSemiAxis, i0 * du + su, j0 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesS,pxSemiAxis,pySemiAxis,pzSemiAxis, i2 * du + su, j0 * dv + sv);
      polygons.push_back(new Polygon(verticesS,NULL));

      std::vector<Vertex*> verticesW;
      CSGMesh::EllipsoidAppendVertex(verticesW,pxSemiAxis,pySemiAxis,pzSemiAxis, i1 * du + su, j1 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesW,pxSemiAxis,pySemiAxis,pzSemiAxis, i0 * du + su, j2 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesW,pxSemiAxis,pySemiAxis,pzSemiAxis, i0 * du + su, j0 * dv + sv);
      polygons.push_back(new Polygon(verticesW,NULL));

      std::vector<Vertex*> verticesE;
      CSGMesh::EllipsoidAppendVertex(verticesE,pxSemiAxis,pySemiAxis,pzSemiAxis,i1 * du + su, j1 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesE,pxSemiAxis,pySemiAxis,pzSemiAxis,i2 * du + su, j0 * dv + sv);
      CSGMesh::EllipsoidAppendVertex(verticesE,pxSemiAxis,pySemiAxis,pzSemiAxis,i2 * du + su, j2 * dv + sv);
      polygons.push_back(new Polygon(verticesE,NULL));
    }
  }

  CSG* mesh = CSG::fromPolygons(polygons);

  Vector* topNorm = new Vector(0.0,0.0,1.0);
  Vector* botNorm = new Vector(0.0,0.0,-1.0);

  G4Plane* pTopCut_temp = new G4Plane("pTopCut",topNorm,pzTopCut);
  G4Plane* pBotCut_temp = new G4Plane("pBottomCut",botNorm,pzBottomCut);

  CSG* pTopCut = pTopCut_temp->GetMesh();
  CSG* pBottomCut = pBotCut_temp->GetMesh();

  mesh = mesh->Subtract(pBottomCut)->Subtract(pTopCut);
  return mesh;
}
