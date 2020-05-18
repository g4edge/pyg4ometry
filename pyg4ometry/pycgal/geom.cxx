//
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` geom.cxx -o geom`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m
//

#include <cmath>
#include "geom.h"

std::ios_base::Init toEnsureInitialization;

/*********************************************
Vector
*********************************************/
Vector::Vector() 
{
  _x = _y = _z = 0;
}
  
Vector::Vector(double x, double y, double z) 
{
  _x = x;
  _y = y;
  _z = z;
}

Vector::Vector(py::list list)
{
  _x = list[0].cast<double>();
  _y = list[1].cast<double>();
  _z = list[2].cast<double>();
}

Vector::Vector(py::tuple tuple)
{
  _x = tuple[0].cast<double>();
  _y = tuple[1].cast<double>();
  _z = tuple[2].cast<double>();
}

Vector::Vector(py::array_t<double> array) 
{
  py::buffer_info buf = array.request();
  
  if (buf.ndim != 1)
    throw std::runtime_error("numpy.ndarray dims must be 1");
  
  if (buf.shape[0] != 3) 
    throw std::runtime_error("numpy.ndarray must be length 3");      
  
  double* ptr = (double*)buf.ptr;
  _x = ptr[0];
  _y = ptr[1];
  _z = ptr[2];    
}
  

Vector::~Vector() {};
  
double Vector::x() {
  return _x;
}

double Vector::y() {
  return _y;
}

double Vector::z() {
  return _z;
} 

Vector Vector::operator+(const Vector &v) const { 
  return Vector(_x + v._x, 
		_y + v._y,
		_z + v._z); 
}

Vector Vector::operator-(const Vector &v) const { 
  return Vector(_x - v._x, 
		_y - v._y,
		_z - v._z); 
} 
Vector Vector::operator*(double value) const { 
  return Vector(_x * value, 
		_y * value,
		_z * value); 
}
  
Vector operator*(double value, const Vector &v) {
  return Vector(value * v._x, value * v._y, value * v._z);
}

Vector operator-(const Vector &v) {
  return Vector(-v._x, -v._y, -v._z);
}

Vector Vector::operator/(double value) const {
  return Vector(_x / value, 
		_y / value,
		_z / value); 
}

double Vector::dot(const Vector v) {
  return _x*v._x + _y*v._y + _z*v._z;
}

Vector Vector::scale(const Vector v) {
  return Vector(_x*v._x, _y*v._y, _z*_z);
}

Vector Vector::lerp(const Vector v, double t) {
  return (*this)+t*(v-(*this));
}

double Vector::length() {
  return sqrt(pow(_x,2) + pow(_y,2) + pow(_z,2));
}

Vector Vector::unit() {
  return (*this)/this->length();
}

Vector Vector::cross(const Vector v) {
  return Vector(_y * v._z - _z * v._y,
		_z * v._x - _x * v._z,
		_x * v._y - _y * v._x);
}

Vector Vector::transform(const double m[3][3]) {
  return Vector(m[0][0] * _x+ m[0][1] * _y + m[0][2] * _z,
		m[1][0] * _x+ m[1][1] * _y + m[1][2] * _z,
		m[2][0] * _x+ m[2][1] * _y + m[2][2] * _z);		
}

int Vector::len() {
  return 3;
}

std::string Vector::toString() const {
  return "[" + std::to_string(_x) + ", " + std::to_string(_y) + ", " + std::to_string(_z)+"]";
}


/*********************************************
Vertex
*********************************************/
Vertex::Vertex(Vector pos) {
  _pos = Vector(pos);
  _normal = Vector(0, 0, 0);
};

Vertex::Vertex(py::list pos) {
  _pos = Vector(pos);
  _normal = Vector(0, 0, 0);
};

Vertex::Vertex(py::tuple pos) {
  _pos = Vector(pos);
  _normal = Vector(0, 0, 0);
};

Vertex::Vertex(py::array_t<double> pos) {
  _pos = Vector(pos);
  _normal = Vector(0, 0, 0);
};


Vertex::Vertex(Vector pos, Vector normal) {
  _pos = Vector(pos);
  _normal = Vector(normal);
}

Vertex::Vertex(py::list pos, py::list normal) {
  _pos = Vector(pos);
  _normal = Vector(normal);
};

Vertex::~Vertex() {};
Vector Vertex::pos() {return _pos;}
Vector Vertex::normal() {return _normal;}

Polygon::Polygon(py::list &vertices) {
  _vertices = vertices;
} 

Polygon::~Polygon(){}

py::list Polygon::vertices() {
  return _vertices;
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(geom, m) {
  py::class_<Vector>(m,"Vector")
    .def(py::init<>())
    .def(py::init<double, double, double>())
    .def(py::init<py::list>())
    .def(py::init<py::tuple>())
    .def(py::init<py::array_t<double>>())
    .def("x", &Vector::x)
    .def("y", &Vector::y)
    .def("z", &Vector::z)
    .def(py::self + py::self)
    .def(py::self - py::self)
    .def(py::self * double())
    .def(double() * py::self)    
    .def(-py::self)
    .def(py::self / double())
    .def("dot", &Vector::dot)
    .def("scale", &Vector::scale)
    .def("lerp", &Vector::lerp)
    .def("length", &Vector::length)
    .def("unit", &Vector::unit)
    .def("cross", &Vector::cross)
	 // .def("transform", &Vector::transform)
    .def("__len__", &Vector::len)
    .def("__repr__", &Vector::toString)
    .def_readwrite("x",&Vector::_x)
    .def_readwrite("y",&Vector::_y)
    .def_readwrite("z",&Vector::_z);

  py::class_<Vertex>(m,"Vertex")
    .def(py::init<Vector>())
    .def(py::init<py::list>())
    .def(py::init<py::tuple>())
    .def(py::init<py::array_t<double>>())
    .def(py::init<Vector, Vector>())
    .def(py::init<py::list, py::list>())
    .def("pos",&Vertex::pos)
    .def("normal",&Vertex::normal)
    .def_readwrite("pos",&Vertex::_pos)
    .def_readwrite("normal",&Vertex::_normal);

  py::class_<Polygon>(m,"Polygon")
    .def(py::init<py::list &>())
    .def("vertices", &Polygon::vertices)
    .def_readwrite("vertices",&Polygon::_vertices);
}

