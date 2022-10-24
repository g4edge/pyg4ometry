#include "geom.h"
/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(geom, m) {
  py::class_<Vector>(m,"Vector")
    .def(py::init<>())
    .def(py::init<double, double, double>())
    .def(py::init<py::list>())
    .def(py::init<py::tuple>())
    .def(py::init<py::array_t<double>>())
    .def("x", &Vector::x)
    .def("y", &Vector::y)
    .def("z", &Vector::z)
    .def(py::self + py::self)
    .def(py::self - py::self)
    .def(py::self * double())
    .def(double() * py::self)
    .def(-py::self)
    .def(py::self / double())
    .def("dot", &Vector::dot)
    .def("scale", &Vector::scale)
    .def("lerp", &Vector::lerp)
    .def("length", &Vector::length)
    .def("unit", &Vector::unit)
    .def("cross", &Vector::cross)
	 // .def("transform", &Vector::transform)
    .def("__len__", &Vector::len)
    .def("__repr__", &Vector::toString)
    .def("__getitem__", &Vector::get)
    .def("__setitem__", &Vector::set)
    .def_readwrite("x",&Vector::_x)
    .def_readwrite("y",&Vector::_y)
    .def_readwrite("z",&Vector::_z);

  py::class_<Vertex>(m,"Vertex")
    .def(py::init<Vector>())
    .def(py::init<py::list>())
    .def(py::init<py::tuple>())
    .def(py::init<py::array_t<double>>())
    .def(py::init<Vector, Vector>())
    .def(py::init<py::list, py::list>())
    .def_readwrite("pos",&Vertex::_pos)
    .def_readwrite("normal",&Vertex::_normal)
    .def("__repr__", &Vertex::toString);

  py::class_<Plane>(m,"Plane")
    .def(py::init<>())
    .def(py::init<Vector &, Vector &, Vector &>())
    .def(py::init<Vertex &, Vertex &, Vertex &>())
    .def_readwrite("normal",&Plane::_normal)
    .def_readwrite("w",&Plane::_w);

  py::class_<Polygon>(m,"Polygon")
    .def(py::init<py::list &>())
    .def("vertices", &Polygon::vertices)
    .def_readwrite("vertices",&Polygon::_vertices)
    .def_readwrite("plane",&Polygon::_plane);
}