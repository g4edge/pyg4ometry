#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TDataStd_GenericExtString.hxx>
#include <TDataStd_TreeNode.hxx>
#include <TDataStd_Name.hxx>
#include <TDataStd_UAttribute.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TDataStd, m) {
  py::class_<TDataStd_GenericExtString, opencascade::handle<TDataStd_GenericExtString>, TDF_Attribute>(m,"TDataStd_GenericExtString")
    .def("ID", &TDataStd_GenericExtString::ID)
    .def("Get",&TDataStd_GenericExtString::Get)
    .def("Set",&TDataStd_GenericExtString::Set);

  py::class_<TDataStd_TreeNode, opencascade::handle<TDataStd_TreeNode>, TDF_Attribute>(m,"TDataStd_TreeNode")
    .def(py::init<>())
    .def("Dump",[](TDataStd_TreeNode &treeNode) {treeNode.Dump(std::cout);})
    .def("DumpJson",[](TDataStd_TreeNode &treeNode) {treeNode.DumpJson(std::cout);})
    .def_static("GetDefaultTreeID",TDataStd_TreeNode::GetDefaultTreeID)
    .def("ID",&TDataStd_TreeNode::ID);

  py::class_<TDataStd_Name,opencascade::handle<TDataStd_Name>, TDataStd_GenericExtString>(m, "TDataStd_Name")
    .def(py::init([](){return opencascade::handle<TDataStd_Name>(new TDataStd_Name());}))
    .def("ID", &TDataStd_Name::ID)
    .def("Dump",[](TDataStd_Name &name) { py::scoped_ostream_redirect output; name.Dump(std::cout);})
    .def_static("GetID",&TDataStd_Name::GetID);

  py::class_<TDataStd_UAttribute, opencascade::handle<TDataStd_UAttribute>, TDF_Attribute>(m,"TDataStd_UAttribute")
    .def(py::init<>())
    .def("Dump",[](TDataStd_UAttribute &uattribute) {uattribute.Dump(std::cout);})
    .def("DumpJson",[](TDataStd_UAttribute &uattribute) {uattribute.DumpJson(std::cout);})
    .def("ID",&TDataStd_UAttribute::ID);
}