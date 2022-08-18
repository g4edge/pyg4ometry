#include <iostream>
#include <fstream>
#include <list>

/* Kernels */
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Exact_integer.h>
#include <CGAL/Extended_homogeneous.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

/* 3D objects */
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Surface_mesh.h>

#include <CGAL/number_utils.h>
#include <CGAL/boost/graph/iterator.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/boost/graph/convert_nef_polyhedron_to_polygon_mesh.h>

#include <CGAL/convex_decomposition_3.h> 

/* IO */
#include <CGAL/IO/Nef_polyhedron_iostream_3.h>
//#include <CGAL/IO/Polyhedron_iostream_3.h>
//#include <CGAL/IO/Surface_mesh_iostream_3.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel                              Kernel;
typedef Kernel::Point_3                                                                Point;
typedef Kernel::Vector_3                                                               Vector;
typedef CGAL::Polyhedron_3<Kernel>                                                     Polyhedron;
typedef CGAL::Nef_polyhedron_3<Kernel>                                                 Nef_polyhedron;
typedef Nef_polyhedron::Aff_transformation_3                                           Aff_transformation_3;
typedef CGAL::Surface_mesh<Kernel::Point_3>                                            Surface_mesh;
typedef Polyhedron::HalfedgeDS                                                         HalfedgeDS;

namespace PMP = CGAL::Polygon_mesh_processing;

#define SUCCESS 0
#define FAILURE 1

template <class HDS> class Build_Polygon_VertexFacet : public CGAL::Modifier_base<HDS> 
{

private: 
  int        nVert;
  int        nFacet;
  double   **vertList;
  long int  *nVertFacet;
  long int **facetList;
  
public:
  Build_Polygon_VertexFacet(int nVertIn, int nFacetIn, double **vertListIn, 
			    long int *nVertFacetIn, long int **facetListIn) 
  {
    nVert     = nVertIn;
    nFacet    = nFacetIn;
    vertList  = vertListIn;
    nVertFacet= nVertFacetIn;
    facetList = facetListIn;
  }
  
  void operator()( HDS& hds) 
  {
    // Postcondition: hds is a valid polyhedral surface.
    CGAL::Polyhedron_incremental_builder_3<HDS> B( hds, true);

    B.begin_surface( nVert, nFacet);
    
    typedef typename HDS::Vertex   Vertex;
    typedef typename Vertex::Point Point;
    
    for(int iVert=0;iVert < nVert; iVert++) {
      B.add_vertex( Point(vertList[iVert][0], vertList[iVert][1], vertList[iVert][2]));
    }

    for(int iFacet=0;iFacet < nFacet; iFacet++) {
      B.begin_facet();
      for(int iFacetVertex=0;iFacetVertex<nVertFacet[iFacet];iFacetVertex++) {
	B.add_vertex_to_facet(facetList[iFacet][iFacetVertex]);
      }
     B.end_facet();
    }

    B.end_surface();
  }
};

int main() 
{
  Polyhedron polyhedron = Polyhedron();

  std::ifstream in("test.pol");
  in >> polyhedron;
  std::cout << "loaded" << std::endl;

  std::cout << "valid " <<  (int)polyhedron.is_valid(false) << std::endl;


  Nef_polyhedron nef_polyhedron = Nef_polyhedron(polyhedron);
  std::cout << "nef" << std::endl;

}

