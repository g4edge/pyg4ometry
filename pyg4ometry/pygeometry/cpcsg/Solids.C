#include "Solids.h"
#include <math.h>
#include <vector>

CSG* Solids::Box(double dx, double dy, double dz) {
  std::vector<Polygon*> polygons;

  Vertex* v1 = new Vertex(new Vector(-dx/2,-dy/2,-dz/2));
  Vertex* v2 = new Vertex(new Vector(-dx/2, dy/2,-dz/2));
  Vertex* v3 = new Vertex(new Vector( dx/2, dy/2,-dz/2));
  Vertex* v4 = new Vertex(new Vector( dx/2,-dy/2,-dz/2));

  Vertex* v5 = new Vertex(new Vector(-dx/2,-dy/2, dz/2));
  Vertex* v6 = new Vertex(new Vector(-dx/2, dy/2, dz/2));
  Vertex* v7 = new Vertex(new Vector( dx/2, dy/2, dz/2));
  Vertex* v8 = new Vertex(new Vector( dx/2,-dy/2, dz/2));
  
  std::vector<Vertex*> f1;
  f1.push_back(v1);
  f1.push_back(v5);
  f1.push_back(v6);
  f1.push_back(v2);

  std::vector<Vertex*> f2;
  f2.push_back(v1);
  f2.push_back(v4);
  f2.push_back(v8);
  f2.push_back(v5);

  std::vector<Vertex*> f3;
  f3.push_back(v1);
  f3.push_back(v2);
  f3.push_back(v3);
  f3.push_back(v4);

  std::vector<Vertex*> f4;
  f4.push_back(v3);
  f4.push_back(v7);
  f4.push_back(v8);
  f4.push_back(v4);

  std::vector<Vertex*> f5;
  f5.push_back(v2);
  f5.push_back(v6);
  f5.push_back(v7);
  f5.push_back(v3);

  std::vector<Vertex*> f6;
  f6.push_back(v5);
  f6.push_back(v8);
  f6.push_back(v7);
  f6.push_back(v6);

  Polygon *p1 = new Polygon(f1,NULL);
  Polygon *p2 = new Polygon(f2,NULL);
  Polygon *p3 = new Polygon(f3,NULL);
  Polygon *p4 = new Polygon(f4,NULL);
  Polygon *p5 = new Polygon(f5,NULL);
  Polygon *p6 = new Polygon(f6,NULL);

  std::vector<Polygon*> p;
  p.push_back(p1);
  p.push_back(p2);
  p.push_back(p3);
  p.push_back(p4);
  p.push_back(p5);
  p.push_back(p6);
  return CSG::fromPolygons(p);
}

void appendVertex(std::vector<Vertex*> &vertices, double r, double theta, double phi){
  //Vector* norm = new Vector(cos(theta)*sin(phi),sin(theta)*sin(phi),cos(phi)); 
  Vector* norm = new Vector(cos(theta)*sin(phi),cos(phi),sin(theta)*sin(phi)); 
  Vector* pos = new Vector(norm->times(r));
  vertices.push_back(new Vertex(pos,norm));
}

CSG* Solids::Sphere(double r,int slices,int stacks){
  std::vector<Polygon*> polygons;
 
  double dTheta = (M_PI*2.0)/double(slices);
  double dPhi = M_PI/double(stacks);

  int j0 = 0;
  int j1 = 1;
  for(int i0=0;i0<slices;i0++){
    int i1 = i0 + 1;
    std::vector<Vertex*> vertices;
    appendVertex(vertices,r,i0*dTheta,j0*dPhi);
    appendVertex(vertices,r,i1*dTheta,j1*dPhi);
    appendVertex(vertices,r,i0*dTheta,j1*dPhi);
    polygons.push_back(new Polygon(vertices,NULL));
  }

  j0 = stacks-1;
  j1 = j0 + 1;

  for(int i0=0;i0<slices;i0++){
    int i1 = i0 + 1;
    std::vector<Vertex*> vertices;
    appendVertex(vertices,r,i0*dTheta,j0*dPhi);
    appendVertex(vertices,r,i1*dTheta,j0*dPhi);
    appendVertex(vertices,r,i0*dTheta,j1*dPhi);
    polygons.push_back(new Polygon(vertices,NULL));
  }

  for(int j0a = 1;j0a < stacks - 1;j0a++){
    double j1a = double(j0a) + 0.5;
    int j2a = j0a + 1;
    for(int i0a = 0;i0a < slices;i0a++){
      double i1a = double(i0a)+0.5;
      int i2a = i0a + 1;
      std::vector<Vertex*> verticesN;
      appendVertex(verticesN,r, i1a * dTheta, j1a * dPhi);
      appendVertex(verticesN,r, i2a * dTheta, j2a * dPhi);
      appendVertex(verticesN,r, i0a * dTheta, j2a * dPhi);
      polygons.push_back(new Polygon(verticesN,NULL));
      
      std::vector<Vertex*> verticesS;
      appendVertex(verticesS,r, i1a * dTheta, j1a * dPhi);
      appendVertex(verticesS,r, i0a * dTheta, j0a * dPhi);
      appendVertex(verticesS,r, i2a * dTheta, j0a * dPhi);
      polygons.push_back(new Polygon(verticesS,NULL));
       
      std::vector<Vertex*> verticesW;
      appendVertex(verticesW,r, i1a * dTheta, j1a * dPhi);
      appendVertex(verticesW,r, i0a * dTheta, j2a * dPhi);
      appendVertex(verticesW,r, i0a * dTheta, j0a * dPhi);
      polygons.push_back(new Polygon(verticesW,NULL));

      std::vector<Vertex*> verticesE;
      appendVertex(verticesE,r, i1a * dTheta, j1a * dPhi);
      appendVertex(verticesE,r, i2a * dTheta, j0a * dPhi);
      appendVertex(verticesE,r, i2a * dTheta, j2a * dPhi);
      polygons.push_back(new Polygon(verticesE,NULL));
    }

  }
  return CSG::fromPolygons(polygons);
}

Vertex* point_cyl(Vector* axisX,Vector* axisY,Vector* axisZ,Vector* s,Vector* ray,double radius, double stack,double angle,double normalBlend){
  Vector out = (axisX->times(cos(angle))).plus( (axisY->times(sin(angle))) );
  Vector* pos = new Vector( (s->plus(ray->times(stack))).plus(out.times(radius)));
  Vector* normal = new Vector( out.times(1.0-abs(normalBlend)).plus( (axisZ->times(normalBlend)) ) );
  return new Vertex(pos, normal);
}

CSG* Solids::Cylinder(double dz,double r,int slices){
  //Vector* s = new Vector(0.0,-dz/2.0,0.0);
  //Vector* e = new Vector(0.0,dz/2.0,0.0);
  Vector* s = new Vector(0.0,0.0,-dz/2.0);
  Vector* e = new Vector(0.0,0.0,dz/2.0); //May need to change back to Y for geant4 interpretation

  Vector* ray = new Vector(e->minus((*s)));

  Vector* axisZ = new Vector(ray->unit());
  double isY = (abs(axisZ->y())) > 0.5 ? 1.0 : 0.0;
  double nisY = (isY == 1.0) ? 0.0 : 1.0;
  Vector* axisX = new Vector(Vector(isY,nisY,0.).cross((*axisZ)).unit());
  Vector* axisY = new Vector((axisX->cross((*axisZ))).unit());
  Vector* startnorm = new Vector(axisZ->clone());
  startnorm->negated();
  Vertex* start = new Vertex(s,startnorm);
  Vertex* end   = new Vertex(e,new Vector(axisZ->unit()));

  std::vector<Polygon*> polygons;
  double dt = (2.0*M_PI)/double(slices);
  for(int i=0;i<slices;i++){
    double t0 = i*dt;
    int i1 = (i+1)%slices;
    double t1 = i1*dt;
    std::vector<Vertex*> v1(3);
    v1[0] = start->clone();
    v1[1] = point_cyl(axisX,axisY,axisZ,s,ray,r,0.0,t0,-1.);
    v1[2] = point_cyl(axisX,axisY,axisZ,s,ray,r,0.0,t1,-1.);
    polygons.push_back(new Polygon(v1,NULL));

    std::vector<Vertex*> v2(4);
    v2[0] = point_cyl(axisX,axisY,axisZ,s,ray,r,0.0,t1,0.0);
    v2[1] = point_cyl(axisX,axisY,axisZ,s,ray,r,0.0,t0,0.0);
    v2[2] = point_cyl(axisX,axisY,axisZ,s,ray,r,1.0,t0,0.0);
    v2[3] = point_cyl(axisX,axisY,axisZ,s,ray,r,1.0,t1,0.0);
    polygons.push_back(new Polygon(v2,NULL));

    std::vector<Vertex*> v3(3);
    v3[0] = end->clone();
    v3[1] = point_cyl(axisX,axisY,axisZ,s,ray,r,1.0,t1,1.0);
    v3[2] = point_cyl(axisX,axisY,axisZ,s,ray,r,1.0,t0,1.0);
    polygons.push_back(new Polygon(v3,NULL));
  }

  return CSG::fromPolygons(polygons);
}

std::vector<Vector*> point_con(Vector* axisX,Vector* axisY,Vector* axisZ,Vector* s,Vector* ray,double radius,double cosTaperAngle,double sinTaperAngle, double angle){
  std::vector<Vector*> vpos_norm(2);
  Vector out = (axisX->times(cos(angle))).plus( (axisY->times(sin(angle))) );
  vpos_norm[0] = new Vector( (s->plus(out.times(radius))));
  vpos_norm[1] = new Vector(out.times(cosTaperAngle).plus(axisZ->times(sinTaperAngle)));
  return vpos_norm;
}

CSG* Solids::Cone(double dz,double r,int slices){ 
  //Vector* s = new Vector(0.0,-dz/2.0,0.0);
  //Vector* e = new Vector(0.0,dz/2.0,0.0);
  Vector* s = new Vector(0.0,0.0,-dz/2.0);
  Vector* e = new Vector(0.0,0.0,dz/2.0); //May need to change back to Y for geant4 interpretation
  return Solids::Cone(s,e,r,slices);
}


CSG* Solids::Cone(Vector* s, Vector* e,double r,int slices){
  Vector* ray = new Vector(e->minus((*s)));

  Vector* axisZ = new Vector(ray->unit());
  double isY = (abs(axisZ->y())) > 0.5 ? 1.0 : 0.0;
  double nisY = (isY == 1.0) ? 0.0 : 1.0;
  Vector* axisX = new Vector(Vector(isY,nisY,0.).cross((*axisZ)).unit());
  Vector* axisY = new Vector((axisX->cross((*axisZ))).unit());
  Vector* startnorm = new Vector(axisZ->clone());
  startnorm->negated();
  Vertex* start = new Vertex(s,startnorm);
  //Vertex* end   = new Vertex(e,new Vector(axisZ->unit()));

  std::vector<Polygon*> polygons;

  double taperAngle = atan2(r,ray->length());
  double sinTaperAngle = sin(taperAngle);
  double cosTaperAngle = cos(taperAngle);
  double dt = (2.0*M_PI)/double(slices);

  for(int i=0;i<slices;i++){
    double t0 = i*dt;
    int i1 = (i+1)%slices;
    double t1 = i1*dt;
    std::vector<Vector*> point0 = point_con(axisX,axisY,axisZ,s,ray,r,cosTaperAngle,sinTaperAngle,t0);
    std::vector<Vector*> point1 = point_con(axisX,axisY,axisZ,s,ray,r,cosTaperAngle,sinTaperAngle,t1);
    Vector* nAvg = new Vector((point0[1]->plus((*point1[1]))).times(0.5));
    std::vector<Vertex*> vpolyStart(3);
    vpolyStart[0] = start->clone();
    vpolyStart[1] = new Vertex(point0[0],startnorm);
    vpolyStart[2] = new Vertex(point1[0],startnorm);
    polygons.push_back(new Polygon(vpolyStart,NULL));
    
    std::vector<Vertex*> vpolySide(3);
    vpolySide[0] = new Vertex(new Vector(point0[0]->clone()),point0[1]);
    vpolySide[1] = new Vertex(new Vector(e->clone()),nAvg);
    vpolySide[2] = new Vertex(new Vector(point1[0]->clone()),point1[1]);
    polygons.push_back(new Polygon(vpolySide,NULL));
  }
  return CSG::fromPolygons(polygons);


}
