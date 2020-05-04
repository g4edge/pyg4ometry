//
// clang++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` core.cxx -o core`python3-config --extension-suffix` -L/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/ -lpython3.7m
//

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>

namespace py = pybind11;

class CSG {
protected : 
 
public:
  py::list _polygons;
  
  CSG();
  ~CSG();

  static CSG fromPolygons(py::list &polygons);
  
  py::list polygons();

};
