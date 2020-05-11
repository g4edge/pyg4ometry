#ifndef __CORE_H
#define __CORE_H

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>

#include "geom.h"
#include "algo.h"

namespace py = pybind11;

class CSG {
protected : 
 
public:
  SurfaceMesh *_surfacemesh;
  int count;
  
  CSG();
  CSG(py::list &polygons);
  CSG(CSG &csg);
  CSG(SurfaceMesh *mesh);
  ~CSG();
  CSG* clone();

  static CSG* fromPolygons(py::list &polygons);
  
  // py::list polygons();
  void translate(Vector &disp);
  void translate(py::list &disp);
  void translate(py::array_t<double> &disp);
  void rotate(Vector &axis, double angle);
  void rotate(py::list &axis, double angle);
  void scale(double);
  py::list* toVerticesAndPolygons();
  void toCGALSurfaceMesh(py::list &polygons);
  CSG* unioN(CSG &csg);
  CSG* subtract(CSG &csg);
  CSG* intersect(CSG &csg);
  SurfaceMesh& getSurfaceMesh();
  int getNumberPolys();
  bool isNull() { return getNumberPolys() == 0; }
};

#endif
