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

  Vector();   
  Vector(double x, double y, double z);
  Vector(py::list list);
  Vector(py::array_t<double> array); 

  ~Vector();
  
  double x();
  double y();
  double z();

  Vector operator+(const Vector &v) const;
  Vector operator-(const Vector &v) const;
  Vector operator*(double value) const;
  
  friend Vector operator*(double value, const Vector &v);
  friend Vector operator-(const Vector &v);
  Vector operator/(double value) const;
  double dot(const Vector v);
  Vector scale(const Vector v);
  Vector lerp(const Vector v, double t);
  double length();
  Vector unit(); 
  Vector cross(const Vector v);
  Vector transform(const double[3][3]);
  int len();
  std::string toString() const;

};

class Vertex {
protected:

public:
  Vector _pos;
  Vector _normal;

  Vertex(Vector pos);
  Vertex(Vector pos, Vector normal);
  ~Vertex();
  Vector pos();
  Vector normal();
};

class Polygon {

public:
  py::list _vertices;

  Polygon(py::list &vertices);
  ~Polygon();
  py::list vertices();
};


#endif
