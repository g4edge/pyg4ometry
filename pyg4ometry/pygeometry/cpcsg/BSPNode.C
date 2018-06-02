#include "BSPNode.h"

BSPNode::BSPNode(){
  plane = NULL;
  front = NULL;
  back = NULL;
}

BSPNode::BSPNode(std::vector<Polygon*> &_polygons){
  plane = NULL;
  front = NULL;
  back = NULL;
  build(_polygons);
}

BSPNode::~BSPNode(){
  delete plane;
  delete front;
  delete back;
  for(int i=0;i<polygons.size();i++){
    delete polygons[i];
  }
  polygons.clear();
}

BSPNode* BSPNode::clone(){
  BSPNode* node = new BSPNode();
  if(plane){
    node->plane = this->plane->clone();
  }
  if(front){
    node->front = this->front->clone();
  }
  if(back){
    node->back = this->back->clone();
  }
  if(polygons.size() > 0){
    std::vector<Polygon*> npolygons;
    for(unsigned i=0;i<polygons.size();i++){
      npolygons.push_back(polygons[i]->clone());
    }
    node->polygons = npolygons;
  }
  return node;
}

void BSPNode::invert(){
  for(unsigned i=0;i<polygons.size();i++){
    polygons[i]->flip();
  }
  plane->flip();
  if(front){
    front->invert();
  }
  if(back){
    back->invert();
  }
  BSPNode* temp = front;
  front = back;
  back = temp;
}
    
std::vector<Polygon*> BSPNode::clipPolygons(std::vector<Polygon*> &_polygons){
  if(!plane){
    return _polygons; 
  }
  std::vector<Polygon*> _front;
  std::vector<Polygon*> _back;
  for(unsigned i=0;i<_polygons.size();i++){
    plane->splitPolygon(_polygons[i],_front,_back,_front,_back);
  }
  if(front){
    _front = front->clipPolygons(_front);
  }
  if(back){
    _back = back->clipPolygons(_back);
  }
  else{
    for(int i=0;i<_back.size();i++){
      delete _back[i];
    }
    _back.clear();
  }
  _front.insert(_front.end(),_back.begin(),_back.end());
  return _front;
}

void BSPNode::clipTo(BSPNode *bsp){
  polygons = bsp->clipPolygons(polygons);
  if(front){
    front->clipTo(bsp);
  }
  if(back){
    back->clipTo(bsp);
  }
}

std::vector<Polygon*> BSPNode::allPolygons(){
  std::vector<Polygon*> _polygons = this->polygons;
  if(front){
    std::vector<Polygon*> _frontpoly = front->allPolygons();
    _polygons.insert(_polygons.end(),_frontpoly.begin(),_frontpoly.end());
  }
  if(back){
    std::vector<Polygon*> _backpoly = back->allPolygons();
    _polygons.insert(_polygons.end(),_backpoly.begin(),_backpoly.end());
  }
  return _polygons;
}

void BSPNode::build(std::vector<Polygon*> _polygons){
  if(_polygons.size() == 0){
    return;
  }
  if(!plane){
    plane = _polygons[0]->GetPlane()->clone();
  }
  polygons.push_back(_polygons[0]);
  std::vector<Polygon*> _front;
  std::vector<Polygon*> _back;
  for(unsigned i = 1;i<_polygons.size();i++){
    plane->splitPolygon(_polygons[i],polygons,polygons,_front,_back);
  }
  if(_front.size() > 0){
    if(!front){
      front = new BSPNode();
    } 
    front->build(_front);
  }
  if(_back.size() > 0){
    if(!back){
      back = new BSPNode();
    }
    back->build(_back);
  } 
}

