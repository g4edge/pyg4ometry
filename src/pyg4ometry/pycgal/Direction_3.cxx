#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Direction_3 Direction_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Direction_3 Direction_3_EPECK;

PYBIND11_MODULE(Direction_3, m) {

  py::class_<Direction_3_EPICK>(m, "Direction_3_EPICK")
      /* Creation */
      .def(py::init<const Kernel_EPICK::Vector_3>())
      .def(py::init<const Kernel_EPICK::Line_3>())
      .def(py::init<const Kernel_EPICK::Ray_3>())
      .def(py::init<const Kernel_EPICK::Segment_3>())
      .def(py::init<const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT>())

      /* Operations */
      .def("delta", &Direction_3_EPICK::delta)
      .def("dx", [](Direction_3_EPICK &d3) { return CGAL::to_double(d3.dx()); })
      .def("dy", [](Direction_3_EPICK &d3) { return CGAL::to_double(d3.dy()); })
      .def("dz", [](Direction_3_EPICK &d3) { return CGAL::to_double(d3.dz()); })
      .def("__eq__", [](const Direction_3_EPICK &d1,
                        const Direction_3_EPICK &d2) { return d1 == d2; })
      .def("__ne__", [](const Direction_3_EPICK &d1,
                        const Direction_3_EPICK &d2) { return d1 != d2; })
      .def("__neg__", [](const Direction_3_EPICK &d) { return -d; })
      .def("vector", &Direction_3_EPICK::vector)
      .def("transform", &Direction_3_EPICK::transform)

      /* pbind11 only */
      .def("__str__", [](Direction_3_EPICK &d1) {
        std::stringstream ss;
        ss << "Direction_3_EPECK : " << CGAL::to_double(d1.dx()) << " "
           << CGAL::to_double(d1.dy()) << " " << CGAL::to_double(d1.dz());
        return ss.str();
      });

  py::class_<Direction_3_EPECK>(m, "Direction_3_EPECK")
      /* Creation */
      .def(py::init<const Kernel_EPECK::Vector_3>())
      .def(py::init<const Kernel_EPECK::Line_3>())
      .def(py::init<const Kernel_EPECK::Ray_3>())
      .def(py::init<const Kernel_EPECK::Segment_3>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT>())

      /* Operations */
      .def("delta", &Direction_3_EPECK::delta)
      .def("dx", &Direction_3_EPECK::dx)
      .def("dy", &Direction_3_EPECK::dy)
      .def("dz", &Direction_3_EPECK::dz)
      .def("dx", [](Direction_3_EPECK &d3) { return CGAL::to_double(d3.dx()); })
      .def("dy", [](Direction_3_EPECK &d3) { return CGAL::to_double(d3.dy()); })
      .def("dz", [](Direction_3_EPECK &d3) { return CGAL::to_double(d3.dz()); })
      .def("__eq__", [](const Direction_3_EPECK &d1,
                        const Direction_3_EPECK &d2) { return d1 == d2; })
      .def("__ne__", [](const Direction_3_EPECK &d1,
                        const Direction_3_EPECK &d2) { return d1 != d2; })
      .def("__neg__", [](const Direction_3_EPECK &d) { return -d; })
      .def("vector", &Direction_3_EPECK::vector)
      .def("transform", &Direction_3_EPECK::transform)

      /* pbind11 only */
      .def("__str__", [](Direction_3_EPECK &d1) {
        std::stringstream ss;
        ss << "Direction_3_EPECK : " << CGAL::to_double(d1.dx()) << " "
           << CGAL::to_double(d1.dy()) << " " << CGAL::to_double(d1.dz());
        return ss.str();
      });
}
