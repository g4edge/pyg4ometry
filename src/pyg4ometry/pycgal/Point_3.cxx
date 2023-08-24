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
typedef Kernel_EPICK::Point_3 Point_3_EPICK;
typedef Kernel_EPICK::Vector_3 Vector_3_EPICK;

typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel_EPECK;
typedef Kernel_EPECK::Point_3 Point_3_EPECK;
typedef Kernel_EPECK::Vector_3 Vector_3_EPECK;

typedef CGAL::Exact_rational ER;
typedef CGAL::Extended_cartesian<ER> Kernel_ECER;
typedef Kernel_ECER::Point_3 Point_3_ECER;
typedef Kernel_ECER::Vector_3 Vector_3_ECER;

PYBIND11_MODULE(Point_3, m) {

  py::class_<Point_3_EPICK>(m, "Point_3_EPICK")

      /* Related functions */
      .def("__lt__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 < p2; })
      .def("__gt__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 > p2; })
      .def("__le__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 <= p2; })
      .def("__ge__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 >= p2; })
      .def("__sub__", [](const Point_3_EPICK &p1,
                         const Point_3_EPICK &p2) { return p1 - p2; })
      .def("__add__", [](const Point_3_EPICK &p1,
                         const Vector_3_EPICK &v2) { return p1 + v2; })
      .def("__sub__", [](const Point_3_EPICK &p1,
                         const Vector_3_EPICK &v2) { return p1 - v2; })

      /* Creation */
      .def(py::init<>())
      .def(py::init<int, int, int>())
      .def(py::init<double, double, double>())
      .def(py::init<Kernel_EPICK::RT, Kernel_EPICK::RT, Kernel_EPICK::RT,
                    Kernel_EPICK::RT>())
      .def(py::init<Kernel_EPICK::FT, Kernel_EPICK::FT, Kernel_EPICK::FT>())

      /* Operations */
      .def("__eq__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 == p2; })
      .def("__ne__", [](const Point_3_EPICK &p1,
                        const Point_3_EPICK &p2) { return p1 != p2; })
      .def("__iadd__",
           [](Point_3_EPICK &p1, const Vector_3_EPICK &v2) {
             p1 += v2;
             return p1;
           })
      .def("__isub__",
           [](Point_3_EPICK &p1, const Vector_3_EPICK &v2) {
             p1 -= v2;
             return p1;
           })

      /* Coordinate Access */
      .def("hx", [](Point_3_EPICK &p3) { return p3.hx(); })
      .def("hy", [](Point_3_EPICK &p3) { return p3.hy(); })
      .def("hz", [](Point_3_EPICK &p3) { return p3.hz(); })
      .def("hw", [](Point_3_EPICK &p3) { return p3.hw(); })
      .def("x", [](Point_3_EPICK &p3) { return p3.x(); })
      .def("y", [](Point_3_EPICK &p3) { return p3.y(); })
      .def("z", [](Point_3_EPICK &p3) { return p3.z(); })

      /* Convenience Operators */
      .def("homogeneous", &Point_3_EPICK::homogeneous)
      .def("cartesian", &Point_3_EPICK::cartesian)
      .def("__getitem__", [](const Point_3_EPICK &p1, int i) { return p1[i]; })
      .def("cartesian_begin",
           [](Point_3_EPICK &p3) { std::cout << "use cartesian_iter\n"; })
      .def("cartesian_end",
           [](Point_3_EPICK &p3) { std::cout << "use cartesian_iter\n"; })
      .def(
          "cartesian_iter",
          [](Point_3_EPICK &p3) {
            return py::make_iterator(p3.cartesian_begin(), p3.cartesian_end());
          },
          py::keep_alive<0, 1>())
      .def("dimension", &Point_3_EPICK::dimension)
      .def("bbox", &Point_3_EPICK::bbox)
      .def("transform", &Point_3_EPICK::transform)

      /* pbind11 only */
      .def("__str__", [](Point_3_EPICK &p1) {
        std::stringstream ss;
        ss << "Point_3_EPICK : " << CGAL::to_double(p1.x()) << " "
           << CGAL::to_double(p1.y()) << " " << CGAL::to_double(p1.y());
        return ss.str();
      });

  py::class_<Point_3_EPECK>(m, "Point_3_EPECK")

      /* Related functions */
      .def("__lt__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 < p2; })
      .def("__gt__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 > p2; })
      .def("__le__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 <= p2; })
      .def("__ge__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 >= p2; })
      .def("__sub__", [](const Point_3_EPECK &p1,
                         const Point_3_EPECK &p2) { return p1 - p2; })
      .def("__add__", [](const Point_3_EPECK &p1,
                         const Vector_3_EPECK &v2) { return p1 + v2; })
      .def("__sub__", [](const Point_3_EPECK &p1,
                         const Vector_3_EPECK &v2) { return p1 - v2; })

      /* Creation */
      .def(py::init<>())
      .def(py::init<int, int, int>())
      .def(py::init<double, double, double>())
      .def(py::init<Kernel_EPECK::RT, Kernel_EPECK::RT, Kernel_EPECK::RT,
                    Kernel_EPECK::RT>())
      .def(py::init<Kernel_EPECK::FT, Kernel_EPECK::FT, Kernel_EPECK::FT>())

      /* Operations */
      .def("__eq__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 == p2; })
      .def("__ne__", [](const Point_3_EPECK &p1,
                        const Point_3_EPECK &p2) { return p1 != p2; })
      .def("__iadd__",
           [](Point_3_EPECK &p1, const Vector_3_EPECK &v2) {
             p1 += v2;
             return p1;
           })
      .def("__isub__",
           [](Point_3_EPECK &p1, const Vector_3_EPECK &v2) {
             p1 -= v2;
             return p1;
           })

      /* Coordinate Access */
      .def("hx", [](Point_3_EPECK &p3) { return p3.hx(); })
      .def("hy", [](Point_3_EPECK &p3) { return p3.hy(); })
      .def("hz", [](Point_3_EPECK &p3) { return p3.hz(); })
      .def("hw", [](Point_3_EPECK &p3) { return p3.hw(); })
      .def("x", [](Point_3_EPECK &p3) { return p3.x(); })
      .def("y", [](Point_3_EPECK &p3) { return p3.y(); })
      .def("z", [](Point_3_EPECK &p3) { return p3.z(); })

      /* Convenience Operators */
      .def("homogeneous", &Point_3_EPECK::homogeneous)
      .def("cartesian", &Point_3_EPECK::cartesian)
      .def("__getitem__", [](const Point_3_EPECK &p1, int i) { return p1[i]; })
      .def("cartesian_begin",
           [](Point_3_EPECK &p3) { std::cout << "use cartesian_iter\n"; })
      .def("cartesian_end",
           [](Point_3_EPECK &p3) { std::cout << "use cartesian_iter\n"; })
      .def(
          "cartesian_iter",
          [](Point_3_EPECK &p3) {
            return py::make_iterator(p3.cartesian_begin(), p3.cartesian_end());
          },
          py::keep_alive<0, 1>())
      .def("dimension", &Point_3_EPECK::dimension)
      .def("bbox", &Point_3_EPECK::bbox)
      .def("transform", &Point_3_EPECK::transform)

      /* pbind11 only */
      .def("__str__", [](Point_3_EPECK &p1) {
        std::stringstream ss;
        ss << "Point_3_EPECK : " << CGAL::to_double(p1.x()) << " "
           << CGAL::to_double(p1.y()) << " " << CGAL::to_double(p1.y());
        return ss.str();
      });

  py::class_<Point_3_ECER>(m, "Point_3_ECER")
      .def(py::init<>())
      .def(py::init<double, double, double>());
}
