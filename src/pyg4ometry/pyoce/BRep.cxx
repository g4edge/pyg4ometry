#include <pybind11/iostream.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

#include <BRep_Builder.hxx>
#include <BRep_Tool.hxx>
#include <Standard_Version.hxx>
#include <TopLoc_Location.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Face.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(BRep, m) {

  py::class_<BRep_Builder, TopoDS_Builder>(m, "BRep_Builder").def(py::init<>());

  py::class_<BRep_Tool>(m, "BRep_Tool")
      .def_static("Surface",
                  [](const TopoDS_Face &F, TopLoc_Location &L) {
                    return BRep_Tool::Surface(F, L);
                  })
      .def_static("Surface",
                  [](const TopoDS_Face &F) { return BRep_Tool::Surface(F); })
      .def_static("Curve",
                  [](const TopoDS_Edge &E, TopLoc_Location &L,
                     Standard_Real &First, Standard_Real &Last) {
                    auto ret = BRep_Tool::Curve(E, L, First, Last);
                    return py::make_tuple(ret, L, First, Last);
                  })
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
      .def_static("Triangulation", &BRep_Tool::Triangulation);
#else

  .def_static("Triangulation",
    [](TopoDS_Face &fac, TopLoc_Location &loc, unsigned int) {
      return BRep_Tool::Triangulation(fac,loc);
    });
#endif
}
