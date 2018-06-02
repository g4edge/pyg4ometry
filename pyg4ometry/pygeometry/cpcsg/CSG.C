#include "CSG.h"
#include <math.h>
#include <map>
#include <fstream>

CSG::CSG(){
  
}
CSG::~CSG(){
  for(unsigned i=0;i<polygons.size();i++){
    delete polygons[i];
  }
  polygons.clear();
}

CSG* CSG::fromPolygons(std::vector<Polygon*> _polygons){
  CSG* csg = new CSG();
  csg->polygons = _polygons;
  return csg;
} 

CSG* CSG::clone(){
  CSG* newcsg = new CSG();
  std::vector<Polygon*> npolygons(this->polygons.size());
  for(unsigned i=0;i<this->polygons.size();i++){
    npolygons[i] = this->polygons[i]->clone();
  }
  newcsg->polygons = npolygons;
  return newcsg;
} 

std::vector<Polygon*> CSG::toPolygons(){
  return this->polygons;
}

CSG* CSG::refine(){
  CSG* newCSG = new CSG();
  for(unsigned i=0;i<this->polygons.size();i++){
    std::vector<Vertex*> verts = polygons[i]->GetVertices();
    unsigned numVerts = polygons[i]->size();
    if(numVerts == 0){
      continue;
    }
    Vector * midPos = new Vector(0.0,0.0,0.0);
    for(int j=0;j<numVerts;j++){
      (*midPos) += (*verts[j]->position());
    }
    (*midPos) /= double(numVerts);
    Vertex* midVert;
    Vector* midNormal;
    if(verts[0]->normal()){
      midNormal = (polygons[i]->GetPlane())->normal();
      midVert = new Vertex(midPos,midNormal);
    } 
    else{
      midVert = new Vertex(midPos);
    }
    std::vector<Vertex*> newVerts = verts;
    for(int j=0;j<numVerts;j++){
      newVerts.push_back(verts[j]->interpolate(verts[(i+1)%numVerts],0.5));
    }
    newVerts.push_back(midVert);
    std::vector<Vertex*> vs(4);
    vs[0] = newVerts[0];
    vs[1] = newVerts[numVerts];
    vs[2] = newVerts[2*numVerts];
    vs[3] = newVerts[2*numVerts-1];
    
    Polygon* newPoly = new Polygon(vs,polygons[i]->GetShared());
    newPoly->SetPlane(polygons[i]->GetPlane());
    newCSG->polygons.push_back(newPoly);

    for(int j=1;j<numVerts;j++){
      vs[0] = newVerts[j];
      vs[1] = newVerts[numVerts+j];
      vs[2] = newVerts[2*numVerts];
      vs[3] = newVerts[numVerts+j-1];
      newPoly = new Polygon(vs,polygons[i]->GetShared());
      newCSG->polygons.push_back(newPoly);
    }
    
  }
  return newCSG;
}

void CSG::translate(Vector* disp){
  for(int i=0;i<polygons.size();i++){
    for(int j=0;j<polygons[i]->size();j++){
      (*polygons[i]->GetVertex(j)->position()) += (*disp);
    }
  }
}

void CSG::scale(Vector* scale){
  for(int i=0;i<polygons.size();i++){
    for(int j=0;j<polygons[i]->vertices.size();j++){
      polygons[i]->GetVertex(j)->position()->scale(scale);
    }
  }
}

Vector* CSG::newVector(Vector* v,Vector* axis,double angleDeg){
  double cosAngle = cos(M_PI*angleDeg/180.);
  double sinAngle = sin(M_PI*angleDeg/180.);
  Vector ax = axis->unit();

  double vA = v->dot(ax);
  Vector vPerp = v->minus(ax.times(vA));
  double vPerpLen = vPerp.length();
  if(vPerpLen == 0){
    //Vector is parallel to axis, no need to rotate
    return v;
  }
  Vector u1 = vPerp.unit();
  Vector u2 = u1.cross(ax);
  double vCosA = vPerpLen*cosAngle;
  double vSinA = vPerpLen*sinAngle;
  return new Vector(ax.times(vA).plus(u1.times(vCosA).plus(u2.times(vSinA))));
}

void CSG::rotate(Vector* axis,double angleDeg){
  for(int i=0;i<polygons.size();i++){
    for(int j=0;j<polygons[i]->vertices.size();j++){
      polygons[i]->vertices[j]->position(newVector(polygons[i]->vertices[j]->position(),axis,angleDeg));
      if(polygons[i]->vertices[j]->normal()->length() > 0){
        polygons[i]->vertices[j]->normal(newVector(polygons[i]->vertices[j]->normal(),axis,angleDeg));
      }
    }
  }
}

VertsAndPolys CSG::toVerticesAndPolygons(){
  //TO DO investigate potential speed increases with large meshes
  std::vector<std::vector<unsigned> > polys;
  int count = 0;

  std::vector<Vertex*> unique_verts;

  double diff = 1.0E-10;
  for(int i=0;i<polygons.size();i++){
    std::vector<unsigned> cell(polygons[i]->vertices.size()); 
    for(int j=0;j<polygons[i]->vertices.size();j++){

      if(unique_verts.size() == 0){
        unique_verts.push_back(polygons[i]->vertices[j]);
      }

      for(int k=0;k<unique_verts.size();k++){
        if(fabs(polygons[i]->vertices[j]->position()->x()-unique_verts[k]->position()->x()) > diff){
          unique_verts.push_back(polygons[i]->vertices[j]);
          break;
        }
        if(fabs(polygons[i]->vertices[j]->position()->y()-unique_verts[k]->position()->y()) > diff){
          unique_verts.push_back(polygons[i]->vertices[j]);
          break;
        }       
        if(fabs(polygons[i]->vertices[j]->position()->z()-unique_verts[k]->position()->z()) > diff){
          unique_verts.push_back(polygons[i]->vertices[j]);
          break;
        }
      }
      unsigned index = unique_verts.size()-1;
      cell[j] = index;
      count++;

    }
    polys.push_back(cell);
  }
  VertsAndPolys vandps;
  vandps.verts = unique_verts;
  vandps.polys = polys;
  vandps.count = count;
  return vandps;
}

void CSG::saveVTK(std::string filename){
  //Save polygons in VTK file.
  std::ofstream f(filename); 
  f << "# vtk DataFile Version 3.0" << std::endl;
  f << "cpcsg output" << std::endl;
  f << "ASCII" << std::endl;
  f << "DATASET POLYDATA" << std::endl;

  VertsAndPolys vandps = this->toVerticesAndPolygons();
  f << "POINTS " << vandps.verts.size() << " float" << std::endl;
  for(int i=0;i<vandps.verts.size();i++){
    f << vandps.verts[i]->position()->x() << " " << vandps.verts[i]->position()->y()<< " " << vandps.verts[i]->position()->z() << std::endl;
  }
  int numCells = vandps.polys.size();
  f << "POLYGONS " << numCells << " " << vandps.count+numCells << std::endl;
  for(int i=0;i<vandps.polys.size();i++){
    f << vandps.polys[i].size() << " ";
    for(int j=0;j<vandps.polys[i].size();j++){
      f << vandps.polys[i][j] << " ";
    }
    f << std::endl;
  }
  f.close();
}
    
CSG* CSG::Union(CSG* csg){
/*
Return a new CSG solid representing space in either this solid or in the
solid `csg`. Neither this solid nor the solid `csg` are modified.::

    A.Union(B)

    +-------+            +-------+
    |       |            |       |
    |   A   |            |       |
    |    +--+----+   =   |       +----+
    +----+--+    |       +----+       |
         |   B   |            |       |
         |       |            |       |
         +-------+            +-------+
*/
  BSPNode* a = new BSPNode((this->clone())->polygons);
  BSPNode* b = new BSPNode((csg->clone())->polygons);
  a->clipTo(b);
  b->clipTo(a);
  b->invert();
  b->clipTo(a);
  b->invert();
  a->build(b->allPolygons());
  return CSG::fromPolygons(a->allPolygons());
}

CSG* CSG::operator+(CSG* csg){
  return this->Union(csg);
}
    
CSG* CSG::Subtract(CSG* csg){
/*
Return a new CSG solid representing space in this solid but not in the
solid `csg`. Neither this solid nor the solid `csg` are modified.::

    A.Subtract(B)

    +-------+            +-------+
    |       |            |       |
    |   A   |            |       |
    |    +--+----+   =   |    +--+
    +----+--+    |       +----+
         |   B   |
         |       |
         +-------+
*/
  BSPNode* a = new BSPNode((this->clone())->polygons);
  BSPNode* b = new BSPNode((csg->clone())->polygons);
  a->invert();
  a->clipTo(b);
  b->clipTo(a);
  b->invert();
  b->clipTo(a);
  b->invert();
  a->build(b->allPolygons());
  a->invert();
  return CSG::fromPolygons(a->allPolygons());
}
    
CSG* CSG::operator-(CSG* csg){
  return this->Subtract(csg);
}


CSG* CSG::Intersect(CSG* csg){
/*
Return a new CSG solid representing space both this solid and in the
solid `csg`. Neither this solid nor the solid `csg` are modified.::

    A.Intersect(B)

    +-------+
    |       |
    |   A   |
    |    +--+----+   =   +--+
    +----+--+    |       +--+
         |   B   |
         |       |
         +-------+
*/
  BSPNode* a = new BSPNode((this->clone())->polygons);
  BSPNode* b = new BSPNode((csg->clone())->polygons);
  a->invert();
  b->clipTo(a);
  b->invert();
  a->clipTo(b);
  b->clipTo(a);
  a->build(b->allPolygons());
  a->invert();
  return CSG::fromPolygons(a->allPolygons());
}

CSG* CSG::operator*(CSG* csg){
  return this->Intersect(csg);
}

CSG* CSG::Inverse(){
/*
Return a new CSG solid with solid and empty space switched. This solid is
not modified.
*/
  CSG* csg = this->clone();
  for(int i=0;i<csg->polygons.size();i++){
    csg->polygons[i]->flip();
  }
  return csg;
}

/*    static CSG* cube();
    static CSG* sphere();
    static CSG* cylinder();
    static CSG* cone();*/


