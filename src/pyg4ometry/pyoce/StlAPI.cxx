#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

namespace py = pybind11;

#include <StlAPI_Writer.hxx>
#include <TopoDS_Shape.hxx>

/*********************************************
PYBIND
*********************************************/
PYBIND11_DECLARE_HOLDER_TYPE(T, opencascade::handle<T>, true)

PYBIND11_MODULE(StlAPI, m) {
  py::class_<StlAPI_Writer>(m,"StlAPI_Writer")
    .def(py::init<>())
    .def("Write",[](StlAPI_Writer &stlw,
                    const TopoDS_Shape &shape,
                    const Standard_CString fileName,
                    const Message_ProgressRange &processRange) {py::scoped_ostream_redirect output;
                                                                std::cout << fileName << std::endl;
                                                                stlw.Write(shape,fileName);});
}