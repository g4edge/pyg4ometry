#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <Message_ProgressRange.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(Message, m) {
  py::class_<Message_ProgressRange> (m,"Message_ProgressRange")
    .def(py::init<>());
}