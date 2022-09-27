#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Geom_Geometry.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pnt.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(Geom, m) {

  py::class_<Geom_Geometry, opencascade::handle<Geom_Geometry>>(m,"Geom_Geometry");
  py::class_<Geom_Curve, opencascade::handle<Geom_Curve>, Geom_Geometry>(m,"Geom_Curve")
    .def("Value",&Geom_Curve::Value);
}