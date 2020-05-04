//
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` geom.cxx -o geom`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m
//

#include <cmath>

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

class Vector {
protected : 
  double _x;
  double _y;
  double _z;
  
public:
  Vector() 
  {
    _x = _y = _z = 0;
  }
  
  Vector(double x, double y, double z) 
  {
    _x = x;
    _y = y;
    _z = z;
  }

  Vector(py::list list)
  {
    _x = list[0].cast<double>();
    _y = list[1].cast<double>();
    _z = list[2].cast<double>();
  }

  Vector(py::array_t<double> array) 
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
  

  ~Vector() {};
  
  double x() {
    return _x;
  }

  double y() {
    return _y;
  }

  double z() {
    return _z;
  } 

  Vector operator+(const Vector &v) const { 
    return Vector(_x + v._x, 
		  _y + v._y,
		  _z + v._z); 
  }
  Vector operator-(const Vector &v) const { 
    return Vector(_x - v._x, 
		  _y - v._y,
		  _z - v._z); 
  } 
  Vector operator*(double value) const { 
    return Vector(_x * value, 
		  _y * value,
		  _z * value); 
  }
  
  friend Vector operator*(double value, const Vector &v) {
    return Vector(value * v._x, value * v._y, value * v._z);
  }

  friend Vector operator-(const Vector &v) {
    return Vector(-v._x, -v._y, -v._z);
  }

  Vector operator/(double value) const {
    return Vector(_x / value, 
		  _y / value,
		  _z / value); 
  }

  double dot(const Vector v) {
    return _x*v._x + _y*v._y + _z*v._z;
  }

  Vector scale(const Vector v) {
    return Vector(_x*v._x, _y*v._y, _z*_z);
  }

  Vector lerp(const Vector v, double t) {
    return (*this)+t*(v-(*this));
  }

  double length() {
    return sqrt(pow(_x,2) + pow(_y,2) + pow(_z,2));
  }

  Vector unit() {
    return (*this)/this->length();
  }

  Vector cross(const Vector v) {
    return Vector(_y * v._z - _z * v._y,
		  _z * v._x - _x * v._z,
		  _x * v._y - _y * v._x);
  }

  int len() {
    return 3;
  }

  std::string toString() const {
    return "[" + std::to_string(_x) + ", " + std::to_string(_y) + ", " + std::to_string(_z)+"]";
  }

};

class Vertex {
protected:
  Vector _pos;
  Vector _normal;

public:
  Vertex(Vector pos) {_pos = Vector(pos);};
  Vertex(Vector pos, Vector normal) {
    _pos = Vector(pos);
    _normal = Vector(normal);
  }
  ~Vertex() {};
  Vector pos() {return _pos;}
  Vector normal() {return _normal;}
};


PYBIND11_MODULE(geom, m) {
  py::class_<Vector>(m,"Vector")
    .def(py::init<>())
    .def(py::init<double, double, double>())
    .def(py::init<py::list>())
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
    .def("__len__", &Vector::len)
    .def("__repr__", &Vector::toString);

  py::class_<Vertex>(m,"Vertex")
    .def(py::init<Vector>())
    .def(py::init<Vector, Vector>())
    .def("pos",&Vertex::pos)
    .def("normal",&Vertex::normal);
}

