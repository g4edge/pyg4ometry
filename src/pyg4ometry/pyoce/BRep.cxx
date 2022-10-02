#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <BRep_Tool.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Edge.hxx>
#include <TopLoc_Location.hxx>
#include <Poly_MeshPurpose.hxx>

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
    .def_static("Triangulation",[](TopoDS_Face &fac, TopLoc_Location &loc, Poly_MeshPurpose) {BRep_Tool::Triangulation(fac,loc,Poly_MeshPurpose_NONE);});
#endif
}