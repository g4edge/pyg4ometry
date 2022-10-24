#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <TCollection_AsciiString.hxx>
#include <TCollection_ExtendedString.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(TCollection, m) {
  py::class_<TCollection_AsciiString>(m,"TCollection_AsciiString")
    .def(py::init<>())
    .def(py::init<const Standard_CString>())
    .def(py::init<const Standard_CString, const Standard_Integer>())
    .def(py::init<const Standard_Character>())
    .def(py::init<const Standard_Integer, const Standard_Character>())
    .def(py::init<const Standard_Integer>())
    .def(py::init<const Standard_Real>())
    .def(py::init<const TCollection_AsciiString &>())
    .def("ToCString",&TCollection_AsciiString::ToCString);

  py::class_<TCollection_ExtendedString>(m,"TCollection_ExtendedString")
    .def(py::init<>())
    .def(py::init<const Standard_CString, const Standard_Boolean>())
    .def(py::init<const Standard_ExtString>())
    .def(py::init<const Standard_Character>())
    .def(py::init<const Standard_ExtCharacter>())
    .def(py::init<const Standard_Integer, const Standard_ExtCharacter>())
    .def(py::init<const Standard_Integer>())
    .def(py::init<const Standard_Real>())
    .def(py::init<const TCollection_ExtendedString>())
    .def(py::init<const TCollection_AsciiString &>())
    .def("Length",&TCollection_ExtendedString::Length)
    .def("Print",[](TCollection_ExtendedString &string) {py::scoped_ostream_redirect output; string.Print(std::cout);})
    .def("ToExtString",&TCollection_ExtendedString::ToExtString);

}


