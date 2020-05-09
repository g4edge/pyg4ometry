#ifndef __CORE_H
#define __CORE_H

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>

#include "geom.h"

namespace py = pybind11;

class CSG {
protected : 
 
public:
  py::list _polygons;

  std::vector<Vector> _verts;
  std::vector<std::vector<unsigned int>> _polys;
  
  CSG();
  ~CSG();

  static CSG fromPolygons(py::list &polygons);
  
  py::list polygons();
  void translate(Vector &disp);
  void translate(py::list &disp);
  void translate(py::array_t<double> &disp);
  void rotate(Vector &axis, double angle);
  void scale(double);
  void toVerticesAndPolygons();
  void toCGALSurfaceMesh();
  void unioN(CSG &csg);
  void subtract(CSG &csg);
  void intersect(CSG &csg);
};

#endif
