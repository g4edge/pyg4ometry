#ifndef __GEOM_H
#define __GEOM_H

#include <cmath>

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

class Vector {
protected :

public:
  double _x;
  double _y;
  double _z;

  Vector() {_x = 0; _y = 0; _z = 0;};
  Vector(double x, double y, double z) {_x = x; _y = y; _z = z;}
  Vector(py::list list) {
    _x = list[0].cast<double>();
    _y = list[1].cast<double>();
    _z = list[2].cast<double>();
  }
  Vector(py::tuple tuple) {
    _x = tuple[0].cast<double>();
    _y = tuple[1].cast<double>();
    _z = tuple[2].cast<double>();
  }

  Vector(py::array_t<double> array) {
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

  ~Vector() {}

  double x() const {return _x;}
  double y() const {return _y;}
  double z() const {return _z;};
  double get(int i) const  {
    switch (i) {
    case 0:
        return x();
    case 1:
        return y();
    case 2:
        return z();
    default:
        throw std::out_of_range(std::string("index = ") + std::to_string(i));
    }
  }

  void set(int i, double value) {
      switch (i) {
      case 0:
        _x = value;
        break;
      case 1:
        _y = value;
        break;
      case 2:
        _z = value;
        break;
      default:
        throw std::out_of_range(std::string("index = ") + std::to_string(i));
      }
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

  Vector transform(const double m[3][3]) {
    return Vector(m[0][0] * _x+ m[0][1] * _y + m[0][2] * _z,
                  m[1][0] * _x+ m[1][1] * _y + m[1][2] * _z,
                  m[2][0] * _x+ m[2][1] * _y + m[2][2] * _z);
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

public:
  Vector _pos;
  Vector _normal;

  Vertex(Vector pos) {
    _pos = Vector(pos);
    _normal = Vector(0, 0, 0);
  }

  Vertex(py::list pos) {
    _pos = Vector(pos);
    _normal = Vector(0, 0, 0);
  }

  Vertex(py::tuple pos) {
    _pos = Vector(pos);
    _normal = Vector(0, 0, 0);
  }

  Vertex(py::array_t<double> pos) {
    _pos = Vector(pos);
    _normal = Vector(0, 0, 0);
  }

  Vertex(Vector pos, Vector normal) {
    _pos = Vector(pos);
    _normal = Vector(normal);
  }

  Vertex(py::list pos, py::list normal)  {
    _pos = Vector(pos);
    _normal = Vector(normal);
  }

  std::string toString() const {
    return std::string("<Vertex pos=") + pos().toString() + ">";
  }

  ~Vertex() {}

  Vector pos() const { return _pos; }
  Vector normal() const { return _normal; };
};

class Plane {
 public:
  double _w;
  Vector _normal;
  Plane() {
    _normal = Vector(0,0,1);
    _w      = 0;
  }

  Plane(Vector &a, Vector &b, Vector &c) {
    _normal = (b-a).cross(c-a).unit();
    _w  = _normal.dot(a);
  }

  Plane(Vertex &av, Vertex &bv, Vertex &cv) {
    Vector a = av._pos;
    Vector b = bv._pos;
    Vector c = cv._pos;

    _normal = (b-a).cross(c-a).unit();
    _w  = _normal.dot(a);
  }

  ~Plane() {};
};

class Polygon {

public:
  py::list _vertices;
  Plane _plane;

  Polygon(py::list &vertices) {
    _vertices = vertices;
    _plane    = Plane(_vertices[0].cast<Vertex&>(),
                      _vertices[1].cast<Vertex&>(),
                      _vertices[2].cast<Vertex&>());
  }

  ~Polygon() {};

  py::list vertices() {
    return _vertices;
  }
};

#endif