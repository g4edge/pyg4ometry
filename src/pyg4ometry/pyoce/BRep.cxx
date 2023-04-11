#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Standard_Version.hxx>
#include <BRep_Tool.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Edge.hxx>
#include <TopLoc_Location.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(BRep, m) {
  py::class_<BRep_Tool>(m,"BRep_Tool")
    .def_static("Curve",[](const TopoDS_Edge &E, TopLoc_Location &L,
                           Standard_Real &First, Standard_Real &Last)
        {
            auto ret = BRep_Tool::Curve(E,L,First,Last);
            return py::make_tuple(ret,L,First,Last);
        })
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def_static("Triangulation",&BRep_Tool::Triangulation);
#else
    .def_static("Triangulation",[](TopoDS_Face &fac, TopLoc_Location &loc, unsigned int) {return BRep_Tool::Triangulation(fac,loc);});
#endif
}