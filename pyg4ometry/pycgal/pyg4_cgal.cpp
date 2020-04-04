#include <CGAL/Simple_cartesian.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>

typedef CGAL::Simple_cartesian<double> Kernel;
typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef CGAL::Polyhedron_3<Kernel>     Polyhedron;
typedef CGAL::Nef_polyhedron_3<Kernel> Nef_polyhedron;
typedef CGAL::Surface_mesh<K::Point_3> Mesh;
typedef Polyhedron::HalfedgeDS         HalfedgeDS;

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

extern "C" void* pyg4_cgal_vertexfacet_polyhedron(int nVert,
						  int nFacet, 
						  double    **vertList, 
						  long int   *nVertFacet,
						  long int  **facetList) 
{
  Polyhedron *P = new Polyhedron();
  Build_Polygon_VertexFacet<HalfedgeDS> pvf(nVert,nFacet,vertList,nVertFacet,facetList);
  P->delegate(pvf);
  return (void*)(P);
}

extern "C" int pyg4_cgal_delete_polyhedron(void *ptr) 
{
  delete (Polyhedron*)ptr;

  return SUCCESS;
}

extern "C" void* pyg4_cgal_union(void *mesh1In, void *mesh2In) 
{
  Mesh *mesh1 = (Mesh*)mesh1In;
  Mesh *mesh2 = (Mesh*)mesh2In;
  Mesh *out   = new Mesh();
  CGAL::Polygon_mesh_processing::corefine_and_compute_union(*mesh1,*mesh2,*out);
  return (void*)(out);
  return SUCCESS;
}
