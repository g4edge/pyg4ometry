#include "ExtrudedSolid.h"

CSG* CSGMesh::ConstructExtrudedSolid(std::vector<Vector*> pPolygon,std::vector<ZSection> pZslices){
  std::vector<double> zpos;
  std::vector<double> x_offs;
  std::vector<double> y_offs;
  std::vector<double> scale;
  for(int i=0;i<pZslices.size();i++){
    zpos.push_back(pZslices[i].z);
    x_offs.push_back(pZslices[i].offset->x());
    y_offs.push_back(pZslices[i].offset->y());
    scale.push_back(pZslices[i].scale);
  }

  std::vector<Polygon*> polygons;
  Polygon* polygonsT;
  Polygon* polygonsB;

  std::vector<Vertex*> vertT;
  for(int i=pPolygon.size()-1;i>=0;i--){
    vertT.push_back(new Vertex(new Vector(scale.back()*pPolygon[i]->x()+x_offs.back(),scale.back()*pPolygon[i]->y()+y_offs.back(),zpos.back()),NULL));
  }
  polygonsT = new Polygon(vertT,NULL);

  std::vector<Vertex*> vertB;
  for(int i=0;i<pPolygon.size();i++) {
    vertB.push_back(new Vertex(new Vector(scale[0]*pPolygon[i]->x()+x_offs[0],scale[0]*pPolygon[i]->y()+y_offs[0],zpos[0]),NULL));
  }
  polygonsB = new Polygon(vertB,NULL);

  polygons.push_back(polygonsB);

  for(int l=1;l<pZslices.size();l++){
    for(int n=0;n<pPolygon.size();n++){
      int n_up = (n+1)%pPolygon.size();
      std::vector<Vertex*> vert(4);
      vert[0] = new Vertex(new Vector(scale[l]*pPolygon[n]->x()+x_offs[l],scale[l]*pPolygon[n]->y()+y_offs[l],zpos[l]),NULL);
      vert[1] = new Vertex(new Vector(scale[l]*pPolygon[n_up]->x()+x_offs[l],scale[l]*pPolygon[n_up]->y()+y_offs[l],zpos[l]),NULL);
      vert[2] = new Vertex(new Vector(scale[l-1]*pPolygon[n_up]->x()+x_offs[l-1],scale[l-1]*pPolygon[n_up]->y()+y_offs[l-1],zpos[l-1]),NULL);
      vert[3] = new Vertex(new Vector(scale[l-1]*pPolygon[n]->x()+x_offs[l-1],scale[l-1]*pPolygon[n]->y()+y_offs[l-1],zpos[l-1]),NULL);
      polygons.push_back(new Polygon(vert,NULL));
    }
  }
  polygons.push_back(polygonsT);
  return CSG::fromPolygons(polygons);
}
