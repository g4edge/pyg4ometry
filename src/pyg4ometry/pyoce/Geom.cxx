#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <GeomPlate_Surface.hxx>
#include <Geom_BSplineSurface.hxx>
#include <Geom_BezierSurface.hxx>
#include <Geom_BoundedSurface.hxx>
#include <Geom_ConicalSurface.hxx>
#include <Geom_Curve.hxx>
#include <Geom_CylindricalSurface.hxx>
#include <Geom_ElementarySurface.hxx>
#include <Geom_Geometry.hxx>
#include <Geom_OffsetSurface.hxx>
#include <Geom_Plane.hxx>
#include <Geom_RectangularTrimmedSurface.hxx>
#include <Geom_SphericalSurface.hxx>
#include <Geom_Surface.hxx>
#include <Geom_SweptSurface.hxx>
#include <Geom_ToroidalSurface.hxx>
#include <ShapeExtend_CompositeSurface.hxx>

#include <gp_Pnt.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(Geom, m) {
  py::class_<Geom_Geometry, opencascade::handle<Geom_Geometry>>(
      m, "Geom_Geometry");

  py::class_<Geom_Curve, opencascade::handle<Geom_Curve>, Geom_Geometry>(
      m, "Geom_Curve")
      .def("Value", &Geom_Curve::Value);

  py::class_<Geom_Surface, opencascade::handle<Geom_Surface>, Geom_Geometry>(
      m, "Geom_Surface")
      .def("DumpJson",
           [](Geom_Surface &surface) { surface.DumpJson(std::cout); });

  py::class_<GeomPlate_Surface, opencascade::handle<GeomPlate_Surface>,
             Geom_Surface>(m, "GeomPlate_Surface");

  py::class_<Geom_BoundedSurface, opencascade::handle<Geom_BoundedSurface>,
             Geom_Surface>(m, "Geom_BoundedSurface");

  py::class_<Geom_BSplineSurface, opencascade::handle<Geom_BSplineSurface>,
             Geom_BoundedSurface>(m, "Geom_BSplineSurface");

  py::class_<Geom_BezierSurface, opencascade::handle<Geom_BezierSurface>,
             Geom_BoundedSurface>(m, "Geom_BezierSurface");

  py::class_<Geom_RectangularTrimmedSurface,
             opencascade::handle<Geom_RectangularTrimmedSurface>,
             Geom_BoundedSurface>(m, "Geom_RectangularTrimmedSurface");

  py::class_<Geom_ElementarySurface,
             opencascade::handle<Geom_ElementarySurface>, Geom_Surface>(
      m, "Geom_ElementarySurface");

  py::class_<Geom_ConicalSurface, opencascade::handle<Geom_ConicalSurface>,
             Geom_ElementarySurface>(m, "Geom_ConicalSurface");

  py::class_<Geom_CylindricalSurface,
             opencascade::handle<Geom_CylindricalSurface>,
             Geom_ElementarySurface>(m, "Geom_CylindricalSurface");

  py::class_<Geom_Plane, opencascade::handle<Geom_Plane>,
             Geom_ElementarySurface>(m, "Geom_Plane");

  py::class_<Geom_SphericalSurface, opencascade::handle<Geom_SphericalSurface>,
             Geom_ElementarySurface>(m, "Geom_SphericalSurface");

  py::class_<Geom_ToroidalSurface, opencascade::handle<Geom_ToroidalSurface>,
             Geom_ElementarySurface>(m, "Geom_ToroidalSurface");

  py::class_<Geom_OffsetSurface, opencascade::handle<Geom_OffsetSurface>,
             Geom_Surface>(m, "Geom_OffsetSurface");

  py::class_<Geom_SweptSurface, opencascade::handle<Geom_SweptSurface>,
             Geom_Surface>(m, "Geom_SweptSurface");

  py::class_<ShapeExtend_CompositeSurface,
             opencascade::handle<ShapeExtend_CompositeSurface>, Geom_Surface>(
      m, "ShapeExtend_CompositeSurface");
}
