#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>
#include <gp_Dir.hxx>
#include <gp_Trsf.hxx>

#include <sstream>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(gp, m) {

  py::class_<gp_Dir>(m,"gp_Dir")
    .def(py::init<>())
    .def("X",&gp_Dir::X)
    .def("Y",&gp_Dir::Y)
    .def("Z",&gp_Dir::Z)
     .def("__str__",[](gp_Dir &gpdir) {
                        std::stringstream ss;
                        ss << "gp_Pny: " << gpdir.X() << " " << gpdir.Y() << " " << gpdir.Z();
                        return ss.str();
                      })
    ;

  py::class_<gp_Pnt>(m,"gp_Pnt")
    .def(py::init<>())
    .def("Transform",&gp_Pnt::Transform)
    .def("X",&gp_Pnt::X)
    .def("Y",&gp_Pnt::Y)
    .def("Z",&gp_Pnt::Z)
     .def("__str__",[](gp_Pnt &gppnt) {
                        std::stringstream ss;
                        ss << "gp_Pny: " << gppnt.X() << " " << gppnt.Y() << " " << gppnt.Z();
                        return ss.str();
                      })
    ;

  py::class_<gp_XYZ>(m,"gp_XYZ")
    .def(py::init<>())
    .def("X",&gp_XYZ::X)
    .def("Y",&gp_XYZ::Y)
    .def("Z",&gp_XYZ::Z)
    .def("__str__",[](gp_XYZ &gpxyz) {
                     std::stringstream ss;
                     ss << "gp_XYZ: " << gpxyz.X() << " " << gpxyz.Y() << " " << gpxyz.Z();
                     return ss.str();
                   })
    .def("DumpJson",[](gp_XYZ &gpxyz) {py::scoped_ostream_redirect output; gpxyz.DumpJson(std::cout);});

  py::class_<gp_Trsf>(m,"gp_Trsf")
    .def(py::init<>())
    .def("GetRotation",[](gp_Trsf &trsf, gp_XYZ &axis, Standard_Real angle)
                         {
                            auto b = trsf.GetRotation(axis,angle);
                            return py::make_tuple(b,axis,angle);
                         })
    .def("ScaleFactor",&gp_Trsf::ScaleFactor)
    .def("TranslationPart",&gp_Trsf::TranslationPart)
    .def("DumpJson",[](gp_Trsf &gpt) {py::scoped_ostream_redirect output; gpt.DumpJson(std::cout);});
}