#include "core.h"

#include <vector>
#include <map> 
#include <iostream>
#include <fstream>
#include <sstream>
#include <functional>
#include <cmath>

// std::ios_base::Init toEnsureInitialization;

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

CSG::CSG(SurfaceMesh *mesh) {
  _surfacemesh = mesh;
}

CSG::~CSG() {
  //  py::print("CSG::~CSG()");
  delete _surfacemesh;
}

CSG *CSG::clone() {
  // py::print("CSG::clone()");
  return new CSG(*this);
}

CSG* CSG::fromPolygons(py::list &polygons, bool cgalTest) {

  //  py::print("CSG::fromPolygons(py::list &)");
  CSG *csg = new CSG(polygons);

  // ensure surface is triangulated
  csg->_surfacemesh->triangulate_faces();

  // checks on solid
  if(cgalTest) {
    int  i_number_of_border_halfedges = csg->_surfacemesh->number_of_border_halfedges(false);
    bool b_is_closed                  = csg->_surfacemesh->is_closed();             // if(!b_is_closed) {py::print("CSG::fromPolygons(py::list &) not closed");}
    bool b_does_self_intersect        = csg->_surfacemesh->does_self_intersect();   // if(b_does_self_intersect) {py::print("CSG::fromPolygons(py::list &) self intersect"); return csg;}
    bool b_does_bound_a_volume        = csg->_surfacemesh->does_bound_a_volume();   // if(!b_does_bound_a_volume) {py::print("CSG::fromPolygons(py::list &) not bound volume");}
    bool b_is_outward_oriented        = csg->_surfacemesh->is_outward_oriented();   // if(!b_is_outward_oriented) {py::print("CSG::fromPolygons(py::list &) not outward oriented");}

    #ifdef __DEBUG_PYIO__
    py::print("CSG::surfacemesh::number_of_border_halfedges",i_number_of_border_halfedges);
    py::print("CSG::surfacemesh::is_closed",b_is_closed);
    py::print("CSG::surfacemesh::does_self_intersect",b_does_self_intersect);
    py::print("CSG::surfacemesh::does_bound_a_volume",b_does_bound_a_volume);
    py::print("CSG::surfacemesh::is_outward_oriented",b_is_outward_oriented);
    #else
    // these are totally unnecessary but allow us to avoid compiler warnings
    i_number_of_border_halfedges = 0;
    b_is_closed = false;
    b_does_self_intersect = false;
    b_does_bound_a_volume = false;
    b_is_outward_oriented = false;
    #endif
  }

  return csg;
}

void CSG::read(std::string fileName) {
  std::ifstream ifstr(fileName);
  //ifstr >> *_surfacemesh;

 }

void CSG::write(std::string fileName) {
  std::ofstream ofstr(fileName);
  //ofstr << *_surfacemesh;
}

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
  double cosAngle = cos(angleDeg/180.0*M_PI);
  double sinAngle = sin(angleDeg/180.0*M_PI);
  double verSin   = 1-cosAngle;

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
  
  _surfacemesh->transform(rot[0][0],rot[0][1],rot[0][2],
			  rot[1][0],rot[1][1],rot[1][2],
			  rot[2][0],rot[2][1],rot[2][2]);
}

void CSG::rotate(py::list &axis, double angleDeg) {
  Vector vAxis = Vector(axis[0].cast<double>(),
			axis[1].cast<double>(),
			axis[2].cast<double>());
  rotate(vAxis,-angleDeg);
}

void CSG::scale(double xs, double ys, double zs) {
  _surfacemesh->transform(xs ,  0,  0,
			  0  , ys,  0,
			  0  ,  0, zs);
}

void CSG::scale(Vector &scale) {
  this->scale(scale._x, scale._y, scale._z);
}

void CSG::scale(py::list &scale) {
  double xs = scale[0].cast<double>();
  double ys = scale[1].cast<double>();
  double zs = scale[2].cast<double>();  
  this->scale(xs,ys,zs);
}

py::list* CSG::toVerticesAndPolygons() {
  return _surfacemesh->toVerticesAndPolygons();
}

void CSG::toCGALSurfaceMesh(py::list &polygons) {
  
  #ifdef __DEBUG_PYIO__
  py::print("CSG::toCGALSurfaceMesh>");
  #endif

  std::vector<Vector> verts;
  std::vector<std::vector<unsigned int>> polys;
   
  /////////////////////////////////////////////////////////////
  std::hash<std::string> hash;
  std::map<size_t, unsigned int> vertexIndexMap;
  
  unsigned int count = 0;

  //  std::ofstream fout("ra.txt");
  
  double offset = 1.234567890; // gives unique key

  #ifdef __DEBUG_PYIO__
  py::print("CSG::toCGALSurfaceMesh> Loop over vertices");
  #endif

  for(auto polyHandle : polygons) {
    Polygon *poly = polyHandle.cast<Polygon*>();
    
    std::vector<unsigned int> cell; 
    for (auto vertHandle : poly->vertices()) {
      Vertex *vert = vertHandle.cast<Vertex*>(); 

      // coordinates of vertex
      double x = vert->pos().x();
      double y = vert->pos().y();
      double z = vert->pos().z();

      // sign of 0
      if(fabs(x) < 1e-11) x = 0;
      if(fabs(y) < 1e-11) y = 0;
      if(fabs(z) < 1e-11) z = 0;
      
      // create "unique" hash
      std::ostringstream sstream;
      sstream.precision(11);
      sstream << std::fixed;
      sstream << x+offset << " " << y+offset << " " << z+offset;
      size_t posHash = hash(sstream.str());
      
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

  #ifdef __DEBUG_PYIO__
  py::print("CSG::toCGALSurfaceMesh> add verts");
  #endif
  for(auto v : verts) {
    #ifdef __DEBUG_PYIP__
    py::print("CSG::toCGALSurfaceMesh>",v._x,v._y,v._z);
    #endif
    _surfacemesh->add_vertex(v._x,v._y, v._z);
  }
  
  #ifdef __DEBUG_PYIO__
  py::print("CSG::toCGALSurfaceMesh> add faces");
  #endif

  for(auto f : polys) {

    if(f.size() == 3) {      
      _surfacemesh->add_face((size_t)f[0],(size_t)f[1], (size_t)f[2]);
    }
    else if(f.size() == 4) {
      _surfacemesh->add_face((size_t)f[0],(size_t)f[1], (size_t)f[2], (size_t)f[3]);
    }
    else {
      _surfacemesh->add_face(f);
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

CSG* CSG::coplanarIntersection(CSG &csg) {
  return new CSG();
}

CSG* CSG::inverse() {
  _surfacemesh->reverse_face_orientations();
  return this;
}

SurfaceMesh& CSG::getSurfaceMesh() {
  return *_surfacemesh;
}

int CSG::getNumberPolys() {
  return _surfacemesh->number_of_faces();
}

int CSG::vertexCount() {
  return _surfacemesh->number_of_vertices();  
}

int CSG::polygonCount() {
  return _surfacemesh->number_of_faces();
}

double CSG::volume() const {
  auto sm = *(_surfacemesh->_surfacemesh);
  return CGAL::to_double(CGAL::Polygon_mesh_processing::volume(sm));
}

double CSG::area() const {
  auto sm = *(_surfacemesh->_surfacemesh);
  return CGAL::to_double(CGAL::Polygon_mesh_processing::area(sm));
}

std::size_t CSG::hash() const {
  return _surfacemesh->hash();
}

bool do_intersect(CSG const &csg1, CSG const &csg2 ){
  auto sm1 = *(csg1._surfacemesh->_surfacemesh);
  auto sm2 = *(csg2._surfacemesh->_surfacemesh);
  return CGAL::Polygon_mesh_processing::do_intersect(sm1, sm2);
}

std::vector<std::pair<std::size_t, std::size_t>>
intersecting_meshes(py::list const &objects) {
  std::vector<Surface_mesh> surface_meshes;
  surface_meshes.reserve(objects.size());
  for (auto &obj : objects) { // get underlying cgal surface_mesh instances
    CSG *csg = obj.cast<CSG *>();
    surface_meshes.push_back(*(csg->_surfacemesh->_surfacemesh));
  }
  std::vector<std::pair<std::size_t, std::size_t>> output;
  CGAL::Polygon_mesh_processing::intersecting_meshes(
      surface_meshes, std::back_inserter(output));
  return output;
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(core, m) {
  py::class_<CSG>(m,"CSG")
    .def(py::init<>())
    .def(py::init<py::list &>())
    .def(py::init<SurfaceMesh *>())
    .def("clone", &CSG::clone)
    .def("fromPolygons",&CSG::fromPolygons, "from polygons", py::arg("cgalTest") = true)
    .def("translate",(void (CSG::*)(Vector &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::list &)) &CSG::translate)
    .def("translate",(void (CSG::*)(py::array_t<double> &)) &CSG::translate)
    .def("rotate",(void (CSG::*)(Vector&, double)) &CSG::rotate)
    .def("rotate",(void (CSG::*)(py::list&, double)) &CSG::rotate)
    .def("scale",(void (CSG::*)(double, double, double)) &CSG::scale)
    .def("scale",(void (CSG::*)(Vector &)) &CSG::scale)
    .def("scale",(void (CSG::*)(py::list &)) &CSG::scale)
    .def("toVerticesAndPolygons",&CSG::toVerticesAndPolygons)
    .def("toCGALSurfaceMesh",&CSG::toCGALSurfaceMesh)
    .def("union",&CSG::unioN)
    .def("intersect",&CSG::intersect)
    .def("subtract",&CSG::subtract)
    .def("coplanarIntersection",&CSG::coplanarIntersection)
    .def("inverse",&CSG::inverse)
    .def("getSurfaceMesh",&CSG::getSurfaceMesh)
    .def("getNumberPolys",&CSG::getNumberPolys)
    .def("vertexCount",&CSG::vertexCount)
    .def("polygonCount",&CSG::polygonCount)
    .def("isNull",&CSG::isNull)
    .def("volume", &CSG::volume, "Returns the volume of this mesh.")
    .def("area", &CSG::area, "Returns the surface area of this mesh.")
    .def("hash", &CSG::hash, "Returns mesh hash");

  m.def("do_intersect", &do_intersect, "Check intersection for two meshes");
  m.def("intersecting_meshes", &intersecting_meshes, "Find all connections between pairs of meshes");
}
