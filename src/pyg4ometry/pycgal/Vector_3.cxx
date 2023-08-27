#include <sstream>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_rational.h>
#include <CGAL/Extended_cartesian.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_EPICK;
typedef Kernel_EPICK::Vector_3 Vector_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Vector_3 Vector_3_EPECK;

typedef CGAL::Exact_rational ER;
typedef CGAL::Extended_cartesian<ER> Kernel_ECER;
typedef Kernel_ECER::Vector_3 Vector_3_ECER;

PYBIND11_MODULE(Vector_3, m) {
  py::class_<Vector_3_EPICK>(m, "Vector_3_EPICK")
      /* Public member functions */
      .def("squared_length",
           [](Vector_3_EPICK &v3) { return v3.squared_length(); })
      .def("__rmul__",
           [](const Kernel_EPICK::RT &s, Vector_3_EPICK &v) { return s * v; })
      .def("__rmul__",
           [](const Kernel_EPICK::FT &s, Vector_3_EPICK &v) { return s * v; })
      .def("__mul__",
           [](Vector_3_EPICK &v, const Kernel_EPICK::RT &s) { return s * v; })
      .def("__mul__",
           [](Vector_3_EPICK &v, const Kernel_EPICK::FT &s) { return s * v; })

      /* Creation */
      .def(py::init<>())
      .def(py::init<const Kernel_EPICK::Point_3, const Kernel_EPICK::Point_3>())
      .def(py::init<const Kernel_EPICK::Segment_3>())
      .def(py::init<const Kernel_EPICK::Ray_3>())
      .def(py::init<const Kernel_EPICK::Line_3>())
      .def(py::init<int, int, int>())
      .def(py::init<double, double, double>())
      .def(py::init<const Kernel_EPICK::RT, const Kernel_EPICK::RT,
                    const Kernel_EPICK::RT, const Kernel_EPICK::RT>())
      .def(py::init<const Kernel_EPICK::FT, const Kernel_EPICK::FT,
                    const Kernel_EPICK::FT>())

      /* Coordinate Access */
      .def("hx", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.hx()); })
      .def("hy", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.hy()); })
      .def("hz", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.hz()); })
      .def("hw", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.hw()); })
      .def("x", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.x()); })
      .def("y", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.y()); })
      .def("z", [](Vector_3_EPICK &p3) { return CGAL::to_double(p3.z()); })

      /* Convenience Operations */
      .def("homogeneous", &Vector_3_EPICK::homogeneous)
      .def("cartesian", &Vector_3_EPICK::cartesian)
      .def("", [](Vector_3_EPICK &v3, int i) { return v3[i]; })
      .def("cartesian_begin",
           [](Vector_3_EPICK &v3) { std::cout << "use cartesian_iter\n"; })
      .def("cartesian_end",
           [](Vector_3_EPICK &v3) { std::cout << "use cartesian_iter\n"; })
      .def(
          "cartesian_iter",
          [](Vector_3_EPICK &v3) {
            return py::make_iterator(v3.cartesian_begin(), v3.cartesian_end());
          },
          py::keep_alive<0, 1>())
      .def("dimension", &Vector_3_EPICK::dimension)
      .def("transform", &Vector_3_EPICK::transform)
      .def("direction", &Vector_3_EPICK::direction)

      /* Operators */
      .def("__eq__", [](const Vector_3_EPICK &v1,
                        const Vector_3_EPICK &v2) { return v1 == v2; })
      .def("__ne__", [](const Vector_3_EPICK &v1,
                        const Vector_3_EPICK &v2) { return v1 != v2; })
      .def("__add__", [](const Vector_3_EPICK &v1,
                         const Vector_3_EPICK &v2) { return v1 + v2; })
      .def("__add__", [](const Vector_3_EPICK &v1,
                         const Vector_3_EPICK &v2) { return v1 + v2; })
      .def("__iadd__",
           [](Vector_3_EPICK &v1, const Vector_3_EPICK &v2) {
             v1 += v2;
             return v1;
           })
      .def("__sub__", [](const Vector_3_EPICK &v1,
                         const Vector_3_EPICK &v2) { return v1 - v2; })
      .def("__isub__",
           [](Vector_3_EPICK &v1, const Vector_3_EPICK &v2) {
             v1 -= v2;
             return v1;
           })
      .def("__div__", [](const Vector_3_EPICK &v1,
                         const Kernel_EPICK::RT &s) { return v1 / s; })
      .def("__idiv__",
           [](Vector_3_EPICK &v1, const Kernel_EPICK::RT &s) {
             return v1 /= s;
             return v1;
           })
      .def("__mul__", [](const Vector_3_EPICK &v1,
                         const Vector_3_EPICK &v2) { return v1 * v2; })
      .def("__imul__",
           [](Vector_3_EPICK &v1, const Kernel_EPICK::FT &s) {
             v1 *= s;
             return v1;
           })

      /* pbind11 only */
      .def("__str__", [](Vector_3_EPICK &v1) {
        std::stringstream ss;
        ss << "Vector_3_EPECK : " << CGAL::to_double(v1.x()) << " "
           << CGAL::to_double(v1.y()) << " " << CGAL::to_double(v1.y());
        return ss.str();
      });

  py::class_<Vector_3_EPECK>(m, "Vector_3_EPECK")
      /* Public member functions */
      .def("squared_length", &Vector_3_EPECK::squared_length)
      .def("__rmul__",
           [](const Kernel_EPECK::RT &s, Vector_3_EPECK &v) { return s * v; })
      .def("__rmul__",
           [](const Kernel_EPECK::FT &s, Vector_3_EPECK &v) { return s * v; })
      .def("__mul__",
           [](Vector_3_EPECK &v, const Kernel_EPECK::RT &s) { return s * v; })
      .def("__mul__",
           [](Vector_3_EPECK &v, const Kernel_EPECK::FT &s) { return s * v; })

      /* Creation */
      .def(py::init<>())
      .def(py::init<const Kernel_EPECK::Point_3, const Kernel_EPECK::Point_3>())
      .def(py::init<const Kernel_EPECK::Segment_3>())
      .def(py::init<const Kernel_EPECK::Ray_3>())
      .def(py::init<const Kernel_EPECK::Line_3>())
      .def(py::init<int, int, int>())
      .def(py::init<double, double, double>())
      .def(py::init<const Kernel_EPECK::RT, const Kernel_EPECK::RT,
                    const Kernel_EPECK::RT, const Kernel_EPECK::RT>())
      .def(py::init<const Kernel_EPECK::FT, const Kernel_EPECK::FT,
                    const Kernel_EPECK::FT>())

      /* Coordinate Access */
      .def("hx", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.hx()); })
      .def("hy", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.hy()); })
      .def("hz", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.hz()); })
      .def("hw", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.hw()); })
      .def("x", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.x()); })
      .def("y", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.y()); })
      .def("z", [](Vector_3_EPECK &p3) { return CGAL::to_double(p3.z()); })

      /* Convenience Operations */
      .def("homogeneous", &Vector_3_EPECK::homogeneous)
      .def("cartesian", &Vector_3_EPECK::cartesian)
      .def("__getitem__", [](Vector_3_EPECK &v3, int i) { return v3[i]; })
      .def("cartesian_begin",
           [](Vector_3_EPECK &v3) { std::cout << "use cartesian_iter\n"; })
      .def("cartesian_end",
           [](Vector_3_EPECK &v3) { std::cout << "use cartesian_iter\n"; })
      .def(
          "cartesian_iter",
          [](Vector_3_EPECK &v3) {
            return py::make_iterator(v3.cartesian_begin(), v3.cartesian_end());
          },
          py::keep_alive<0, 1>())
      .def("dimension", &Vector_3_EPECK::dimension)
      .def("transform", &Vector_3_EPECK::transform)
      .def("direction", &Vector_3_EPECK::direction)

      /* Operators */
      .def("__eq__", [](const Vector_3_EPECK &v1,
                        const Vector_3_EPECK &v2) { return v1 == v2; })
      .def("__ne__", [](const Vector_3_EPECK &v1,
                        const Vector_3_EPECK &v2) { return v1 != v2; })
      .def("__add__", [](const Vector_3_EPECK &v1,
                         const Vector_3_EPECK &v2) { return v1 + v2; })
      .def("__add__", [](const Vector_3_EPECK &v1,
                         const Vector_3_EPECK &v2) { return v1 + v2; })
      .def("__iadd__",
           [](Vector_3_EPECK &v1, const Vector_3_EPECK &v2) {
             v1 += v2;
             return v1;
           })
      .def("__sub__", [](const Vector_3_EPECK &v1,
                         const Vector_3_EPECK &v2) { return v1 - v2; })
      .def("__isub__",
           [](Vector_3_EPECK &v1, const Vector_3_EPECK &v2) {
             v1 -= v2;
             return v1;
           })
      .def("__div__", [](const Vector_3_EPECK &v1,
                         const Kernel_EPECK::RT &s) { return v1 / s; })
      .def("__idiv__",
           [](Vector_3_EPECK &v1, const Kernel_EPECK::RT &s) {
             return v1 /= s;
             return v1;
           })
      .def("__mul__", [](const Vector_3_EPECK &v1,
                         const Vector_3_EPECK &v2) { return v1 * v2; })
      .def("__imul__",
           [](Vector_3_EPECK &v1, const Kernel_EPECK::FT &s) {
             v1 *= s;
             return v1;
           })

      /* pbind11 only */
      .def("__str__", [](Vector_3_EPECK &v1) {
        std::stringstream ss;
        ss << "Vector_3_EPECK : " << CGAL::to_double(v1.x()) << " "
           << CGAL::to_double(v1.y()) << " " << CGAL::to_double(v1.y());
        return ss.str();
      });

  py::class_<Vector_3_ECER>(m, "Vector_3_ECER")
      .def(py::init<>())
      .def(py::init<double, double, double>());
}
