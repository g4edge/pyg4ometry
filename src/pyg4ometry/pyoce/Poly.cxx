#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Standard_Version.hxx>
#include <Poly_Triangle.hxx>
#include <Poly_Triangulation.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(Poly, m) {
  py::class_<Poly_Triangle>(m,"Poly_Triangle")
    .def(py::init<>())
    .def(py::init<const Standard_Integer, const Standard_Integer, const Standard_Integer>())
    .def("Set",[](Poly_Triangle &tri, const Standard_Integer n1, const Standard_Integer n2, const Standard_Integer n3) {tri.Set(n1,n2,n3);})
    .def("Set",[](Poly_Triangle &tri, const Standard_Integer index, const Standard_Integer node) {tri.Set(index,node);})
    .def("Get",[](Poly_Triangle &tri) {Standard_Integer n1, n2, n3; tri.Get(n1,n2,n3); return py::make_tuple(n1,n2,n3);})
    .def("Value", &Poly_Triangle::Value)
    .def("__call__",[](Poly_Triangle &tri, const Standard_Integer index) {return tri(index);});

  py::class_<Poly_Triangulation, opencascade::handle<Poly_Triangulation>, Standard_Transient>(m, "Poly_Triangulation")
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def(py::init<>())
    .def(py::init<const Standard_Integer, const Standard_Integer, const Standard_Boolean, const Standard_Boolean>())
#else
    .def(py::init([](const Standard_Integer a1, const Standard_Integer a2, const Standard_Boolean a3, const Standard_Boolean a4) {
        return new Poly_Triangulation(a1,a2,a3);
    }))
#endif
    .def("Deflection",[](Poly_Triangulation &pt){return pt.Deflection();})
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("HasGeometry",&Poly_Triangulation::HasGeometry)
#endif
    .def("HasNormals",&Poly_Triangulation::HasNormals)
    .def("HasUVNodes",&Poly_Triangulation::HasUVNodes)
    .def("NbNodes",&Poly_Triangulation::NbNodes)
    .def("NbTriangles",&Poly_Triangulation::NbTriangles)
    .def("Node",&Poly_Triangulation::Node)
    .def("Normal",[](Poly_Triangulation &pt, Standard_Integer i) {return pt.Normal(i);})
#if OCC_VERSION_MAJOR == 7 && OCC_VERSION_MINOR == 6
    .def("SetNode",&Poly_Triangulation::SetNode)
    .def("SetTriangle",&Poly_Triangulation::SetTriangle)
#else
    .def("SetNode",[](Poly_Triangulation &pt, Standard_Integer theIndex, const gp_Pnt &thePnt) {
        pt.ChangeNode(theIndex) = thePnt;
    })
    .def("SetTriangle",[](Poly_Triangulation &pt, Standard_Integer theIndex, const Poly_Triangle &theTri) {
        pt.ChangeTriangle(theIndex) = theTri;
    })
#endif
    .def("Triangle",&Poly_Triangulation::Triangle)
    .def("UVNode",&Poly_Triangulation::Node);

  // Copied from Poly_MeshPurpose.hxx
  enum Poly_MeshPurpose {
    Poly_MeshPurpose_NONE = 0 , Poly_MeshPurpose_Calculation = 0x0001 , Poly_MeshPurpose_Presentation = 0x0002 , Poly_MeshPurpose_Active = 0x0004 ,
    Poly_MeshPurpose_Loaded = 0x0008 , Poly_MeshPurpose_AnyFallback = 0x0010 , Poly_MeshPurpose_USER = 0x0020
  };

  py::enum_<Poly_MeshPurpose>(m,"Poly_MeshPurpose")
    .value("Poly_MeshPurpose_NONE", Poly_MeshPurpose::Poly_MeshPurpose_NONE)
    .value("Poly_MeshPurpose_Calculation", Poly_MeshPurpose::Poly_MeshPurpose_Calculation)
    .value("Poly_MeshPurpose_Presentation", Poly_MeshPurpose::Poly_MeshPurpose_Presentation)
    .value("Poly_MeshPurpose_Active", Poly_MeshPurpose::Poly_MeshPurpose_Active)
    .value("Poly_MeshPurpose_Loaded", Poly_MeshPurpose::Poly_MeshPurpose_Loaded)
    .value("Poly_MeshPurpose_AnyFallback", Poly_MeshPurpose::Poly_MeshPurpose_AnyFallback)
    .value("Poly_MeshPurpose_USER", Poly_MeshPurpose::Poly_MeshPurpose_USER)
    .export_values();
}