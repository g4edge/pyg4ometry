#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <gp_Ax1.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>
#include <gp_Trsf.hxx>
#include <gp_Vec.hxx>

#include <sstream>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(gp, m) {

  py::class_<gp_XYZ>(m, "gp_XYZ")
      .def(py::init<>())
      .def(py::init<const Standard_Real, const Standard_Real,
                    const Standard_Real>())
      .def("X", &gp_XYZ::X)
      .def("Y", &gp_XYZ::Y)
      .def("Z", &gp_XYZ::Z)
      .def("__str__",
           [](gp_XYZ &gpxyz) {
             std::stringstream ss;
             ss << "gp_XYZ: " << gpxyz.X() << " " << gpxyz.Y() << " "
                << gpxyz.Z();
             return ss.str();
           })
      .def("DumpJson", [](gp_XYZ &gpxyz) {
        py::scoped_ostream_redirect output;
        gpxyz.DumpJson(std::cout);
      });

  py::class_<gp_Dir>(m, "gp_Dir")
      .def(py::init<>())
      .def(py::init<const gp_XYZ &>())
      .def(py::init<const Standard_Real, const Standard_Real,
                    const Standard_Real>())
      .def("X", &gp_Dir::X)
      .def("Y", &gp_Dir::Y)
      .def("Z", &gp_Dir::Z)
      .def("__str__", [](gp_Dir &gpdir) {
        std::stringstream ss;
        ss << "gp_Pny: " << gpdir.X() << " " << gpdir.Y() << " " << gpdir.Z();
        return ss.str();
      });

  py::class_<gp_Pnt>(m, "gp_Pnt")
      .def(py::init<>())
      .def(py::init<const Standard_Real, const Standard_Real,
                    const Standard_Real>())
      .def("Transform", &gp_Pnt::Transform)
      .def("X", &gp_Pnt::X)
      .def("Y", &gp_Pnt::Y)
      .def("Z", &gp_Pnt::Z)
      .def("__str__", [](gp_Pnt &gppnt) {
        std::stringstream ss;
        ss << "gp_Pnt: " << gppnt.X() << " " << gppnt.Y() << " " << gppnt.Z();
        return ss.str();
      });

  py::class_<gp_Vec>(m, "gp_Vec")
      .def(py::init<>())
      .def(py::init<const gp_XYZ &>())
      .def(py::init<const Standard_Real, const Standard_Real,
                    const Standard_Real>())
      .def("X", &gp_Vec::X)
      .def("Y", &gp_Vec::Y)
      .def("Z", &gp_Vec::Z)
      .def("__str__", [](gp_Vec &gpvec) {
        std::stringstream ss;
        ss << "gp_Vec: " << gpvec.X() << " " << gpvec.Y() << " " << gpvec.Z();
        return ss.str();
      });

  py::class_<gp_Ax1>(m, "gp_Ax1")
      .def(py::init<>())
      .def(py::init<const gp_Pnt &, const gp_Dir &>());

  py::class_<gp_Trsf>(m, "gp_Trsf")
      .def(py::init<>())
      .def("SetRotation",
           [](gp_Trsf &t, const gp_Ax1 &ax, const Standard_Real ang) {
             t.SetRotation(ax, ang);
           })
      .def("SetTranslationPart", &gp_Trsf::SetTranslationPart)
      .def("SetValues", &gp_Trsf::SetValues)
      .def("GetRotation",
           [](gp_Trsf &trsf, gp_XYZ &axis, Standard_Real angle) {
             auto b = trsf.GetRotation(axis, angle);
             return py::make_tuple(b, axis, angle);
           })
      .def("ScaleFactor", &gp_Trsf::ScaleFactor)
      .def("TranslationPart", &gp_Trsf::TranslationPart)
      .def("DumpJson", [](gp_Trsf &gpt) {
        py::scoped_ostream_redirect output;
        gpt.DumpJson(std::cout);
      });
}
