#ifndef BSPNODE_H
#define BSPNODE_H

#include "Polygon.h"
#include "Plane.h"
#include <vector>

class BSPNode {
  public:
    BSPNode();
    BSPNode(std::vector<Polygon*> &_polygons);
    ~BSPNode();

    BSPNode* clone();
    void invert();
    std::vector<Polygon*> clipPolygons(std::vector<Polygon*> &_polygons);
    void clipTo(BSPNode *bsp);
    std::vector<Polygon*> allPolygons();
    void build(std::vector<Polygon*> _polygons);
  private:
    std::vector<Polygon*> polygons;
    BSPNode* front;
    BSPNode* back;
    Plane* plane;
};

#endif
