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

CSG::CSG() {
  // py::print("CSG::CSG()");
  _surfacemesh = new SurfaceMesh();
}

CSG::CSG(py::list &polygons) {
  // py::print("CSG::CSG(py::list&)");
  _surfacemesh = new SurfaceMesh();
  toCGALSurfaceMesh(polygons);
}

CSG::CSG(CSG &csg) {
  //  py::print("CSG::CSG(CSG&)");
  _surfacemesh = new SurfaceMesh(*(csg._surfacemesh));
}

CSG::CSG(SurfaceMesh* mesh) {
  _surfacemesh = mesh;
}

CSG::~CSG() {
  //  py::print("CSG::~CSG()");
  delete _surfacemesh;
}

CSG *CSG::clone() { return new CSG(*this); }

CSG* CSG::fromPolygons(py::list &polygons) {
  //  py::print("CSG::fromPolygons(py::list &)");
  CSG *csg = new CSG(polygons);
  return csg;
}

//py::list CSG::polygons() {
//  return _polygons;
//}

void CSG::translate(Vector &disp) {
  _surfacemesh->translate(disp._x, disp._y, disp._z);
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

  // std::cout << normAxis.toString() << " " 
  // << cosAngle << " " << sinAngle << " " 
  // << verSin << std::endl;
  
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

  _surfacemesh->transform(rot[0][0],rot[0][1],rot[0][2],
			  rot[1][0],rot[1][1],rot[1][2],
			  rot[2][0],rot[2][1],rot[2][2]);
}

void CSG::rotate(py::list &axis, double angleDeg) {
  Vector vAxis = Vector(axis[0].cast<double>(),
			axis[1].cast<double>(),
			axis[2].cast<double>());
  rotate(vAxis,angleDeg);
}

void CSG::scale(double scale) {
}

py::list* CSG::toVerticesAndPolygons() {
  return _surfacemesh->toVerticesAndPolygons();
}

void CSG::toCGALSurfaceMesh(py::list &polygons) {

  std::vector<Vector> verts;
  std::vector<std::vector<unsigned int>> polys;
   
  /////////////////////////////////////////////////////////////
  std::hash<std::string> hash;
  std::map<size_t, unsigned int> vertexIndexMap;
  
  unsigned int count = 0;

  //  std::ofstream fout("ra.txt");
  
  for(auto polyHandle : polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    
    std::vector<unsigned int> cell; 
    for (auto vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 
      //size_t posHash  = hash(vert->pos().x()) ^ hash(vert->pos().y()) ^ hash(vert->pos().y());
      std::ostringstream sstream;
      sstream << vert->pos().x() << " " << vert->pos().y() << " " << vert->pos().z();
      size_t posHash = hash(sstream.str());
      //fout << vert->pos().x() << " " << vert->pos().y() << " " << vert->pos().z() << " " << posHash << std::endl;
      
      // check if not in in map 
      if (vertexIndexMap.find(posHash) == vertexIndexMap.end()) {
	vertexIndexMap.insert(std::pair<size_t, unsigned int>(posHash,verts.size()));
	verts.push_back(vert->pos());
      }
      
      cell.push_back(vertexIndexMap.find(posHash)->second);
      count++;
    }
    polys.push_back(cell);
  }

  for(auto v : verts) {
    _surfacemesh->add_vertex(v._x,v._y, v._z); 
  }

  for(auto f : polys) {

    if(f.size() == 3) {      
      // py::print((size_t)f[0],(size_t)f[1],(size_t)f[2]);
      _surfacemesh->add_face((size_t)f[0],(size_t)f[1], (size_t)f[2]);
    }
    else if(f.size() == 4) {
      // py::print((size_t)f[0],(size_t)f[1],(size_t)f[2],(size_t)f[3]);
      _surfacemesh->add_face((size_t)f[0],(size_t)f[1], (size_t)f[2], (size_t)f[3]);
    }
  } 
}

CSG* CSG::unioN(CSG &csg) {
  return new CSG(_surfacemesh->unioN(*csg._surfacemesh));
}
CSG* CSG::intersect(CSG &csg) {
  return new CSG(_surfacemesh->intersect(*csg._surfacemesh));
}

CSG* CSG::subtract(CSG &csg) {
  return new CSG(_surfacemesh->subtract(*csg._surfacemesh));
}

SurfaceMesh& CSG::getSurfaceMesh() {
  return *_surfacemesh;
}

int CSG::getNumberPolys() {
  return _surfacemesh->number_of_faces();
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(core, m) {
  py::class_<CSG>(m,"CSG")
    .def(py::init<>())
    .def(py::init<py::list &>())
    .def("clone", &CSG::clone)
    .def("fromPolygons",&CSG::fromPolygons)
    //    .def("polygons",&CSG::polygons)
    .def("translate",(void (CSG::*)(Vector &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::list &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::array_t<double> &)) &CSG::translate)
    .def("rotate",(void (CSG::*)(Vector&, double)) &CSG::rotate)
    .def("rotate",(void (CSG::*)(py::list&, double)) &CSG::rotate)
    .def("scale",&CSG::scale)
    .def("toVerticesAndPolygons",&CSG::toVerticesAndPolygons)
    .def("toCGALSurfaceMesh",&CSG::toCGALSurfaceMesh)
    .def("union",&CSG::unioN)
    .def("intersect",&CSG::intersect)
    .def("subtract",&CSG::subtract)
    .def("getSurfaceMesh",&CSG::getSurfaceMesh)
    .def("getNumberPolys",&CSG::getNumberPolys)
    .def("isNull",&CSG::isNull);
}
