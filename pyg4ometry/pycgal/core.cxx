//
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` core.cxx -o core`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` geom.cpython-37m-darwin.so core.cxx -o core`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m

#include "core.h"

#include <vector>
#include <map> 
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>

std::ios_base::Init toEnsureInitialization;

/*********************************************
CSG
*********************************************/

CSG::CSG() {}

CSG::~CSG() {}

CSG CSG::fromPolygons(py::list &polygons) {
  CSG csg;
  csg._polygons = polygons;
  return csg;
}

py::list CSG::polygons() {
  return _polygons;
}

void CSG::translate(Vector &disp) {
  for (py::handle polyHandle : _polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    for (py::handle vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 
      vert->_pos = vert->_pos + disp;      
    } 
  }
}

void CSG::translate(py::list &disp) {
  Vector v(disp);
  this->translate(v);
}

void CSG::translate(py::array_t<double> &disp) {
  Vector v(disp);
  this->translate(v);
}

void CSG::rotate(Vector &axis, double angleDeg) {
  double rot[3][3];

  // convert axis and angle to matrix
  Vector normAxis = axis/axis.length();
  double cosAngle = cos(angleDeg/180.0*3.14159264);
  double sinAngle = sin(angleDeg/180.0*3.14159264);
  double verSin   = 1-cosAngle;

  // std::cout << normAxis.toString() << " " << cosAngle << " " << sinAngle << " " << verSin << std::endl;
  
  double x = normAxis._x;
  double y = normAxis._y;
  double z = normAxis._z;

  rot[0][0] = (verSin * x * x) + cosAngle;
  rot[0][1] = (verSin * x * y) - (z * sinAngle);
  rot[0][2] = (verSin * x * z) + (y * sinAngle);

  rot[1][0] = (verSin * y * x) + (z * sinAngle);
  rot[1][1] = (verSin * y * y) + cosAngle;
  rot[1][2] = (verSin * y * z) - (x * sinAngle);

  rot[2][0] = (verSin * z * x) - (y * sinAngle);
  rot[2][1] = (verSin * z * y) + (x * sinAngle);
  rot[2][2] = (verSin * z * z) + cosAngle;  
  
  // std::cout << rot[0][0] << " " << rot[0][1] << " " << rot[0][2] << std::endl;
  // std::cout << rot[1][0] << " " << rot[1][1] << " " << rot[1][2] << std::endl;
  // std::cout << rot[2][0] << " " << rot[2][1] << " " << rot[2][2] << std::endl;

  for (py::handle polyHandle : _polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    for (py::handle vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 
      vert->_pos = vert->_pos.transform(rot);
    } 
  }  
}

void CSG::scale(double scale) {
  for (py::handle polyHandle : _polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    for (py::handle vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 
      vert->_pos = vert->_pos * scale;      
    } 
  }
}

void CSG::toVerticesAndPolygons() {

  std::hash<std::string> hash;
  std::map<size_t, unsigned int> vertexIndexMap;
  
  unsigned int count = 0;

  std::ofstream fout("ra.txt");
  
  for(auto polyHandle : _polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    
    std::vector<unsigned int> cell; 
    for (auto vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 
      //size_t posHash  = hash(vert->pos().x()) ^ hash(vert->pos().y()) ^ hash(vert->pos().y());
      std::ostringstream sstream;
      sstream << vert->pos().x() << " " << vert->pos().y() << " " << vert->pos().z();
      size_t posHash = hash(sstream.str());
      fout << vert->pos().x() << " " << vert->pos().y() << " " << vert->pos().z() << " " << posHash << std::endl;
      
      // check if not in in map 
      if (vertexIndexMap.find(posHash) == vertexIndexMap.end()) {
	vertexIndexMap.insert(std::pair<size_t, unsigned int>(posHash,_verts.size()));
	_verts.push_back(vert->pos());
      }
      
      cell.push_back(vertexIndexMap.find(posHash)->second);
      count++;
    }
    _polys.push_back(cell);
  }


  for(auto v : _verts) {
    fout << v.toString() << std::endl;
  }

  for(auto p : _polys) {
    for(auto i : p) {
      fout << i << " ";
    }
    fout << std::endl;
  }
}

void CSG::toCGALSurfaceMesh() {
  
}

void CSG::unioN(CSG &csg) {
}

void CSG::subtract(CSG &csg) {
}

void CSG::intersect(CSG &csg) {

}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(core, m) {
  py::class_<CSG>(m,"CSG")
    .def(py::init<>())
    .def("fromPolygons",&CSG::fromPolygons)
    .def("polygons",&CSG::polygons)
    .def("translate",(void (CSG::*)(Vector &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::list &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::array_t<double> &)) &CSG::translate)
    .def("rotate",&CSG::rotate)
    .def("scale",&CSG::scale)
    .def("toVerticesAndPolygons",&CSG::toVerticesAndPolygons)
    .def("union",&CSG::unioN)
    .def("intersect",&CSG::intersect)
    .def("subtract",&CSG::subtract)
    .def_readwrite("polygons",&CSG::_polygons);
}
