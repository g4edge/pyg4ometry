#include <fstream>

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
namespace py = pybind11;

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>

#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_3.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel                              Kernel_EPECK;
typedef Kernel_EPECK::Point_3                                                          Point_EPECK;
typedef Kernel_EPECK::Vector_3                                                         Vector_EPECK;
typedef CGAL::Polyhedron_3<Kernel_EPECK>                                               Polyhedron_3_EPECK;
typedef Polyhedron_3_EPECK::HalfedgeDS                                                 HalfedgeDS_EPECK;

typedef CGAL::Exact_predicates_inexact_constructions_kernel                            Kernel_EPICK;
typedef Kernel_EPICK::Point_3                                                          Point_EPICK;
typedef Kernel_EPICK::Vector_3                                                         Vector_EPICK;
typedef CGAL::Polyhedron_3<Kernel_EPICK>                                               Polyhedron_3_EPICK;
typedef Polyhedron_3_EPICK::HalfedgeDS                                                 HalfedgeDS_EPICK;

PYBIND11_MAKE_OPAQUE(std::vector<Polyhedron_3_EPICK>);
PYBIND11_MAKE_OPAQUE(std::vector<Polyhedron_3_EPECK>);

template <class HDS> class Build_Polygon_VertexFacet : public CGAL::Modifier_base<HDS>
{
private:
  std::vector<std::vector<double>> verts;
  std::vector<std::vector<int>> faces;

public:
  Build_Polygon_VertexFacet(std::vector<std::vector<double>> &vertsIn,
                            std::vector<std::vector<int>> &facesIn)
  {
    verts = vertsIn;
    faces = facesIn;
  }

  void operator()( HDS& hds)
  {
    // Postcondition: hds is a valid polyhedral surface.
    CGAL::Polyhedron_incremental_builder_3<HDS> B( hds, true);

    B.begin_surface(verts.size(), faces.size(),0, CGAL::Polyhedron_incremental_builder_3<HDS>::RELATIVE_INDEXING);

    typedef typename HDS::Vertex   Vertex;
    typedef typename Vertex::Point Point;

    for(auto v : verts) {
      B.add_vertex( Point(v[0], v[1], v[2]));
    }

    for(auto f : faces) {
      if (f.size() == 3) {
	    B.begin_facet();
	    B.add_vertex_to_facet(f[0]);
	    B.add_vertex_to_facet(f[1]);
	    B.add_vertex_to_facet(f[2]);
	    B.end_facet();
      }
      else if(f.size() == 4) {
	    B.begin_facet();
	    B.add_vertex_to_facet(f[0]);
	    B.add_vertex_to_facet(f[1]);
	    B.add_vertex_to_facet(f[2]);
	    B.add_vertex_to_facet(f[2]);
	    B.end_facet();
	  }
    }
    B.end_surface();
    B.remove_unconnected_vertices();
  }
};

PYBIND11_MODULE(Polyhedron_3, m) {

  py::class_<Polyhedron_3_EPECK>(m,"Polyhedron_3_EPECK")
    .def(py::init<>())
    .def("buildFromVertsAndFaces",[](Polyhedron_3_EPECK &p,
                                      std::vector<std::vector<double>> &verts,
                                      std::vector<std::vector<int>> &faces) {
      Build_Polygon_VertexFacet<HalfedgeDS_EPECK> pvf(verts, faces);
      p.delegate(pvf);
    })

    /* Access member functions */
    .def("empty",&Polyhedron_3_EPECK::empty)
    .def("size_of_vertices",&Polyhedron_3_EPECK::size_of_vertices)
    .def("size_of_halfedges",&Polyhedron_3_EPECK::size_of_halfedges)
    .def("size_of_facets",&Polyhedron_3_EPECK::size_of_facets)
    .def("facets_begin",[](Polyhedron_3_EPECK &p) {return p.facets_begin();})
    .def("facets_end",[](Polyhedron_3_EPECK &p) {return p.facets_end();})
    .def("halfedges_begin",[](Polyhedron_3_EPECK &p) {return p.halfedges_begin();})
    .def("halfedges_end",[](Polyhedron_3_EPECK &p) {return p.halfedges_end();})
    // TDOO Many

    /* Types for Tagging Optional Features */
    .def("Supports_facet_plane",[](Polyhedron_3_EPECK &p) {return Polyhedron_3_EPECK::Supports_facet_plane();})

    /* Combinatorial predicates */
    .def("is_closed",&Polyhedron_3_EPECK::is_closed)
    // TODO these are in latest manual but not my version of CGAL
    //.def("is_pure_bivalent",&Polyhedron_3_EPECK::is_pure_bivalent)
    //.def("is_pure_trivalent",&Polyhedron_3_EPECK::is_pure_trivalent)
    //.def("is_pure_triangle",&Polyhedron_3_EPECK::is_pure_triangle)
    //.def("is_pure_quad",&Polyhedron_3_EPECK::is_pure_quad)
    // TODO is_triangle
    // TODO is_tetrahedron

    /* Miscellaneous */
    .def("inside_out",&Polyhedron_3_EPECK::inside_out)
    .def("is_valid",&Polyhedron_3_EPECK::is_valid)
    .def("normalized_border_is_valid",&Polyhedron_3_EPECK::normalized_border_is_valid)

    /* IO */
    .def("write_OFF",[](Polyhedron_3_EPECK &p, std::string fileName)
    {
        std::ofstream ofstr(fileName.c_str());
        ofstr << p;
        ofstr.close();
    })

    /* TODO find out why facet iterator plane does not work  */
    .def("convertToPlanes",[](Polyhedron_3_EPECK &p) {
      std::vector<std::vector<double>> planes;
      for(auto f = p.facets_begin(); f != p.facets_end() ;++f) {
        auto heh = f->halfedge();
        auto plane = Polyhedron_3_EPECK::Facet::Plane_3(heh->vertex()->point(),
                                                        heh->next()->vertex()->point(),
                                                        heh->next()->next()->vertex()->point());
        auto pp = plane.point();
        auto pn = plane.orthogonal_vector();

        std::vector<double> planeV;
        planeV.push_back(CGAL::to_double(pp.x()));
        planeV.push_back(CGAL::to_double(pp.y()));
        planeV.push_back(CGAL::to_double(pp.z()));

        planeV.push_back(CGAL::to_double(pn.x()));
        planeV.push_back(CGAL::to_double(pn.y()));
        planeV.push_back(CGAL::to_double(pn.z()));

        planes.push_back(planeV);
      }
      return planes;
    });

  py::class_<Polyhedron_3_EPECK::Facet_iterator>(m,"Polyhedron_3_EPECK_Facet_Iterator")
    .def("deref",[](Polyhedron_3_EPECK::Facet_iterator &fi) {return *fi;})
    .def("plane",[](Polyhedron_3_EPECK::Facet_iterator &fh) {
      std::cout << CGAL::to_double(fh->plane().a()) << " " << CGAL::to_double(fh->plane().a()) << " " << CGAL::to_double(fh->plane().c()) << " " << CGAL::to_double(fh->plane().d()) <<std::endl;
      return fh->plane();
    },py::return_value_policy::copy)
    .def("next",[](Polyhedron_3_EPECK::Facet_iterator &fi) {++fi;})
    .def("__ne__",[](Polyhedron_3_EPECK::Facet_iterator fi1, Polyhedron_3_EPECK::Facet_iterator fi2) {return fi1 != fi2;});
  // TODO Plane should be moved to its own class as will clash eventually
  py::class_<Polyhedron_3_EPECK::Facet::Plane_3>(m,"Polyhedron_3_EPECK_Face_Plane_3")
    .def("point",&Polyhedron_3_EPECK::Facet::Plane_3::point, py::return_value_policy::copy)
    .def("orthogonal_vector",&Polyhedron_3_EPECK::Facet::Plane_3::orthogonal_vector, py::return_value_policy::copy)
    .def("a",[](Polyhedron_3_EPECK::Facet::Plane_3 &p3) {return CGAL::to_double(p3.a());})
    .def("b",[](Polyhedron_3_EPECK::Facet::Plane_3 &p3) {return CGAL::to_double(p3.b());})
    .def("c",[](Polyhedron_3_EPECK::Facet::Plane_3 &p3) {return CGAL::to_double(p3.c());})
    .def("d",[](Polyhedron_3_EPECK::Facet::Plane_3 &p3) {return CGAL::to_double(p3.d());});
  py::class_<Polyhedron_3_EPECK::Halfedge_iterator>(m,"Polyhedron_3_EPECK_Halfedge_Iterator");

  py::class_<Polyhedron_3_EPICK>(m,"Polyhedron_3_EPICK")
    .def(py::init<>())
    .def("buildFromVertsAndFaces",[](Polyhedron_3_EPICK &p,
                                      std::vector<std::vector<double>> &verts,
                                      std::vector<std::vector<int>> &faces) {
      Build_Polygon_VertexFacet<HalfedgeDS_EPICK> pvf(verts, faces);
      p.delegate(pvf);
    })

    /* Access member functions */
    .def("empty",&Polyhedron_3_EPICK::empty)
    .def("size_of_vertices",&Polyhedron_3_EPICK::size_of_vertices)
    .def("size_of_halfedges",&Polyhedron_3_EPICK::size_of_halfedges)
    .def("size_of_facets",&Polyhedron_3_EPICK::size_of_facets)
    // TDOO Many

    /* Combinatorial predicates */
    .def("is_closed",&Polyhedron_3_EPICK::is_closed)
    // TODO these are in latest manual but not my version of CGAL
    //.def("is_pure_bivalent",&Polyhedron_3_EPICK::is_pure_bivalent)
    //.def("is_pure_trivalent",&Polyhedron_3_EPICK::is_pure_trivalent)
    //.def("is_pure_triangle",&Polyhedron_3_EPICK::is_pure_triangle)
    //.def("is_pure_quad",&Polyhedron_3_EPICK::is_pure_quad)
    // TODO is_triangle
    // TODO is_tetrahedron

    /* Miscellaneous */
    .def("inside_out",&Polyhedron_3_EPICK::inside_out)
    .def("is_valid",&Polyhedron_3_EPICK::is_valid)
    .def("normalized_border_is_valid",&Polyhedron_3_EPICK::normalized_border_is_valid)

    /* IO */
    .def("write_OFF",[](Polyhedron_3_EPICK &p, std::string fileName)
    {
        std::ofstream ofstr(fileName.c_str());
        ofstr << p;
        ofstr.close();
    });

  py::bind_vector<std::vector<Polyhedron_3_EPECK>>(m, "Vector_Polyhedron_3_EPECK");
  py::bind_vector<std::vector<Polyhedron_3_EPICK>>(m, "Vector_Polyhedron_3_EPICK");

}