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

/* 2D Objects */
#include <CGAL/Partition_traits_2.h>

#include <CGAL/number_utils.h>
#include <CGAL/boost/graph/iterator.h>

/* 3D Algorithms */
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/boost/graph/convert_nef_polyhedron_to_polygon_mesh.h>
#include <CGAL/convex_decomposition_3.h> 

/* 2D Algorithms */
#include <CGAL/partition_2.h>

/* IO */
#include <CGAL/IO/Nef_polyhedron_iostream_3.h>

typedef CGAL::Exact_predicates_exact_constructions_kernel                              Kernel;
typedef Kernel::Point_3                                                                Point;
typedef Kernel::Vector_3                                                               Vector;
typedef CGAL::Polyhedron_3<Kernel>                                                     Polyhedron;
typedef CGAL::Nef_polyhedron_3<Kernel>                                                 Nef_polyhedron;
typedef Nef_polyhedron::Aff_transformation_3                                           Aff_transformation_3;
typedef CGAL::Surface_mesh<Kernel::Point_3>                                            Surface_mesh;
typedef Polyhedron::HalfedgeDS                                                         HalfedgeDS;

typedef CGAL::Partition_traits_2<Kernel>                                               Partition_traits_2;
typedef Partition_traits_2::Point_2                                                    Point_2;
typedef Partition_traits_2::Polygon_2                                                  Polygon_2; 
typedef std::list<Polygon_2>                                                           Polygon_list;

namespace PMP = CGAL::Polygon_mesh_processing;

#define SUCCESS 0
#define FAILURE 1

std::ios_base::Init toEnsureInitialization;

template <class HDS> class Build_Polygon_VertexFacet : public CGAL::Modifier_base<HDS> 
{

private: 
  int        nVert;
  int        nFacet;
  double   **vertList;
  long int  *nVertFacet;
  long int **facetList;
  bool       debugIo;
  
public:
  Build_Polygon_VertexFacet(int nVertIn, 
			    int nFacetIn, 
			    double **vertListIn, 
			    long int *nVertFacetIn, 
			    long int **facetListIn, 
			    bool debugIoIn = false) 
  {
    nVert     = nVertIn;
    nFacet    = nFacetIn;
    vertList  = vertListIn;
    nVertFacet= nVertFacetIn;
    facetList = facetListIn;
    debugIo   = debugIoIn;

    if(debugIo)
      std::cout<< "Build_Polygon_VertexFacet> " << nVert << " " << nFacet << std::endl;
  }
  
  void operator()( HDS& hds) 
  {
    // Postcondition: hds is a valid polyhedral surface.
    CGAL::Polyhedron_incremental_builder_3<HDS> B( hds, true);

    B.begin_surface( nVert, nFacet,0, CGAL::Polyhedron_incremental_builder_3<HDS>::RELATIVE_INDEXING);
    
    typedef typename HDS::Vertex   Vertex;
    typedef typename Vertex::Point Point;
    
    for(int iVert=0;iVert < nVert; iVert++) {
      B.add_vertex( Point(vertList[iVert][0], vertList[iVert][1], vertList[iVert][2]));
      if(debugIo)
	std::cout << "Build_Polygon_VertexFacet> vertex " 
		  << iVert << " "  
		  << vertList[iVert][0] << " "
		  << vertList[iVert][1] << " " 
		  << vertList[iVert][2] << " " 
		  << (int)B.error() << std::endl;
    }

    for(int iFacet=0;iFacet < nFacet; iFacet++) {

      #if 0
      B.begin_facet();
      for(int iVert=0;iVert < nVertFacet[iFacet]; ++iVert) {
	B.add_vertex_to_facet(facetList[iFacet][iVert]);	
      }
      B.end_facet();
      #endif 
      
      # if 1
      if(nVertFacet[iFacet]== 3) {
	B.begin_facet();
	B.add_vertex_to_facet(facetList[iFacet][0]);
	B.add_vertex_to_facet(facetList[iFacet][1]);
	B.add_vertex_to_facet(facetList[iFacet][2]);
	if(debugIo) 
	  std::cout << "Build_Polygon_VertexFacet> triangle " 
		    << facetList[iFacet][0] << " " << facetList[iFacet][1] << " " << facetList[iFacet][2] << " " << (int)B.error() << std::endl;	  
	B.end_facet();
      }
      else if(nVertFacet[iFacet] == 4) {
	B.begin_facet();
	B.add_vertex_to_facet(facetList[iFacet][0]);
	B.add_vertex_to_facet(facetList[iFacet][1]);
	B.add_vertex_to_facet(facetList[iFacet][2]);
	B.end_facet();

	B.begin_facet();
	B.add_vertex_to_facet(facetList[iFacet][0]);
	B.add_vertex_to_facet(facetList[iFacet][2]);
	B.add_vertex_to_facet(facetList[iFacet][3]);
	B.end_facet();
	if(debugIo)
	  std::cout << "Build_Polygon_VertexFacet> quad " 
		    << facetList[iFacet][0] << " " << facetList[iFacet][1] << " " << facetList[iFacet][2] << " " <<  facetList[iFacet][3] << " " << (int)B.error() << std::endl;	  
      }
      #endif
    }
    B.end_surface();
    
    if(debugIo) {
      std::cout << "Build_Polygon_VertexFacet> unconnected " << (int)B.check_unconnected_vertices() << std::endl;
      std::cout << "Build_Polygon_VertexFacet> error       " << (int)B.error() << std::endl;
    }
    B.remove_unconnected_vertices();
  }
};

extern "C" int pyg4_cgal_polyhedron_write(void *polyhedronIn, 
					  char *fileName) 
{
  Polyhedron *poly = (Polyhedron*)polyhedronIn;

  std::ofstream out(fileName);
  out << *poly;
  out.close();
  return SUCCESS;
}

extern "C" int pyg4_cgal_nefpolyhedron_write(void *nefIn, 
					     char*fileName)
{
  Nef_polyhedron *nef = (Nef_polyhedron*)nefIn;

  std::ofstream out(fileName);
  out << *nef;
  out.close();
  return SUCCESS;
}

extern "C" int pyg4_cgal_surfacemesh_write(void *meshIn, 
					   char *fileName) 
{
  Surface_mesh *mesh = (Surface_mesh*)meshIn;

  std::ofstream out(fileName);
  out << *mesh;
  out.close();
  return SUCCESS;
}

extern "C" int pyg4_cgal_polyhedron_print(void *polyhedronIn) 
{
  std::cout << "pyg4_cgal_polyhedron_print>" << std::endl;

  Polyhedron *polyhedron = (Polyhedron*)polyhedronIn;

  printf("pyg4_cgal_polygon_print> vertices\n");
  Polyhedron::Point p;
  for(Polyhedron::Vertex_iterator v = polyhedron->vertices_begin(); 
      v != polyhedron->vertices_end() ; ++v) {
    p = v->point();

    printf("vertex %f %f %f\n",
	   CGAL::to_double(p.x()), 
	   CGAL::to_double(p.y()), 
	   CGAL::to_double(p.z()));
  }

  printf("pyg4_cgal_polygon_print> facets\n");
  int ifacet = 0;
  for(Polyhedron::Facet_iterator f = polyhedron->facets_begin(); f != polyhedron->facets_end(); ++f, ++ifacet) {
    Polyhedron::Halfedge_around_facet_circulator fc = f->facet_begin();
    int ivertex = 0;
    do {
      p = fc->vertex()->point();
      printf("facet %i vertex %i %f %f %f\n",
	     ifacet,
	     ivertex,
	     CGAL::to_double(p.x()), 
	     CGAL::to_double(p.y()), 
	     CGAL::to_double(p.z()));   
      ++ivertex;
    } while( ++fc != f->facet_begin());
  }
  
  return SUCCESS;
}

extern "C" int pyg4_cgal_nefpolyhedron_print(void *nefIn) 
{
  printf("pyg4_cgal_nefpolyhedron_print>\n");  

  //Nef_polyhedron *nef = (Nef_polyhedron*)nefIn;

  return SUCCESS;    
}

extern "C" int pyg4_cgal_surfacemesh_print(void *meshIn) 
{
  printf("pyg4_cgal_surfacemesh_print>\n");

  Surface_mesh *mesh = (Surface_mesh*)meshIn;

  //Surface_mesh::Vertex_range r = mesh->vertices();
  //Surface_mesh::Vertex_range::iterator vb = r.begin();
  //Surface_mesh::Vertex_range::iterator ve = r.end();

  // Loop over vertices
  printf("pyg4_cgal_surfacemesh_print> vertices\n");
  Surface_mesh::Point p;
  for(Surface_mesh::Vertex_index vd : mesh->vertices()){

    p = mesh->point(vd);

    printf("vertex %i %f %f %f\n",
	   (int)vd,
	   CGAL::to_double(p.x()), 
	   CGAL::to_double(p.y()), 
	   CGAL::to_double(p.z()));
  }

  // Loop over faces
  printf("pyg4_cgal_surfacemesh_print> facets\n");
  for(Surface_mesh::Face_index fd : mesh->faces()) {
    printf("face %i ", (int)fd);
    for(Surface_mesh::Halfedge_index hd :  CGAL::halfedges_around_face(mesh->halfedge(fd),*mesh)) {
      printf("%i ", (int)mesh->source(hd));
    }
    printf("\n");
  }

  return SUCCESS;  
}

extern "C" void* pyg4_cgal_vertexfacet_to_polyhedron(int         nVert,
						     int         nFacet, 
						     double    **vertList, 
						     long int   *nVertFacet,
						     long int  **facetList,
						     bool        debugIo) 
{
  Polyhedron *P = new Polyhedron();
  if(debugIo) 
    std::cout << "pyg4_cgal_vertexfacet_to_polyhedron> polyhedron ptr " << P << std::endl;
  Build_Polygon_VertexFacet<HalfedgeDS> pvf(nVert, nFacet, vertList, nVertFacet, facetList, debugIo);
  P->delegate(pvf);
  return (void*)(P);
}

extern "C" int pyg4_cgal_convexpolyhedron_to_planes(void *polyhedronIn, 
						    int *nPlane, 
						    double **planeList,
						    bool debugIo = false)
{
  Polyhedron *polyhedron = (Polyhedron*)polyhedronIn;
  Polyhedron::Facet::Halfedge_handle heh;

  // Form planes for each facet
  int ifacet = 0;
  
  for(Polyhedron::Facet_iterator f = polyhedron->facets_begin(); f != polyhedron->facets_end(); ++f, ++ifacet) {
    heh = f->halfedge();
    Polyhedron::Facet::Plane_3 plane = Polyhedron::Facet::Plane_3(heh->vertex()->point(),
								  heh->next()->vertex()->point(),
								  heh->next()->next()->vertex()->point());
    Point pp = plane.point();
    Vector pn = plane.orthogonal_vector();
    
    planeList[ifacet][0] = CGAL::to_double(pp.x());
    planeList[ifacet][1] = CGAL::to_double(pp.y());
    planeList[ifacet][2] = CGAL::to_double(pp.z());

    planeList[ifacet][3] = CGAL::to_double(pn.x());
    planeList[ifacet][4] = CGAL::to_double(pn.y());
    planeList[ifacet][5] = CGAL::to_double(pn.z());
      

    if(debugIo) 
      std::cout << " pyg4_cgal_convexpolyhedron_to_planes> plane " 
		<< CGAL::to_double(pp.x()) << " "
		<< CGAL::to_double(pp.y()) << " " 
		<< CGAL::to_double(pp.z()) << " "
		<< CGAL::to_double(pn.x()) << " "
		<< CGAL::to_double(pn.y()) << " "
		<< CGAL::to_double(pn.z()) << std::endl;
  }

  *nPlane = ifacet;

  return SUCCESS;
}

extern "C" int pyg4_cgal_delete_polyhedron(void *ptr) 
{
  delete (Polyhedron*)ptr;

  return SUCCESS;
}

extern "C" int pyg4_cgal_delete_nefpolyhedron(void *ptr) 
{
  delete (Nef_polyhedron*)ptr;

  return SUCCESS;
}

extern "C" int pyg4_cgal_delete_surfacemesh(void *ptr) 
{
  delete (Surface_mesh*)ptr;

  return SUCCESS;
}

extern "C" void* pyg4_cgal_polyhedron_to_nefpolyhedron(void *polyhedronIn) 
{
  Polyhedron* polyhedron = (Polyhedron*)polyhedronIn;
  std::cout << "pyg4_cgal_polyhedron_to_nefpolyhedron> polyhedron ptr " << polyhedron << std::endl;

  Nef_polyhedron* nef_polyhedron = new Nef_polyhedron(*polyhedron);
  return (void*)(nef_polyhedron);
}

extern "C" void* pyg4_cgal_nefpolyhedron_to_polyhedron(void *nef_polyhedronIn) 
{
  Nef_polyhedron *nef_polyhedron = (Nef_polyhedron*)nef_polyhedronIn;
  Polyhedron *polyhedron = new Polyhedron();
  nef_polyhedron->convert_to_polyhedron(*polyhedron);
  return (void*)nef_polyhedron;
}

extern "C" void* pyg4_cgal_nefpolyhedron_to_surfacemesh(void *nef_polyhedronIn) 
{
  Nef_polyhedron *nef_polyhedron = (Nef_polyhedron*)nef_polyhedronIn;
  Surface_mesh   *out = new Surface_mesh();
  CGAL::convert_nef_polyhedron_to_polygon_mesh(*nef_polyhedron, *out);
  return (void*)out;
}

/*
extern "C" void* pyg4_cgal_nefpolyhedron_transform(void *nef_polyhendronIn)
{

}
*/

extern "C" void* pyg4_cgal_nefpolyhedron_union(void *nef1In, 
					       void *nef2In) 
{
  Nef_polyhedron* nef1 = (Nef_polyhedron*)nef1In;
  Nef_polyhedron* nef2 = (Nef_polyhedron*)nef2In;
  Nef_polyhedron* out  = new Nef_polyhedron((*nef1)+(*nef2));
  return (void*)out;
}

extern "C" void* pyg4_cgal_nefpolyhedron_intersection(void *nef1In, 
						      void *nef2In) 
{
  Nef_polyhedron* nef1 = (Nef_polyhedron*)nef1In;
  Nef_polyhedron* nef2 = (Nef_polyhedron*)nef2In;
  Nef_polyhedron* out  = new Nef_polyhedron((*nef1)*(*nef2));
  return (void*)out;
}

extern "C" void* pyg4_cgal_nefpolyhedron_subtraction(void *nef1In, 
						     void *nef2In) 
{
  Nef_polyhedron* nef1 = (Nef_polyhedron*)nef1In;
  Nef_polyhedron* nef2 = (Nef_polyhedron*)nef2In;
  Nef_polyhedron* out  = new Nef_polyhedron((*nef1)-(*nef2));
  return (void*)out;
}

extern "C" int pyg4_cgal_nefpolyhedron_to_convexpolyhedra(void *nefIn, 
							  void **polyhedronOut, 
							  int *nConvex) 
{
  Nef_polyhedron* nef = (Nef_polyhedron*)nefIn;
  
  std::cout << "pyg4_cgal_nefpolyhedron_to_convexpolyhedra> nef ptr " << nefIn  << std::endl;


  CGAL::convex_decomposition_3(*nef);
  std::list<Polyhedron*> convex_parts;
  
  // the first volume is the outer volume, which is 
  // ignored in the decomposition
  Nef_polyhedron::Volume_const_iterator ci = ++(*nef).volumes_begin();
  Polyhedron *P;
  for(int i=0 ; ci != (*nef).volumes_end(); ++ci, ++i) {
    if(ci->mark()) {
      P = new Polyhedron();
      (*nef).convert_inner_shell_to_polyhedron(ci->shells_begin(), *P);
      convex_parts.push_back(P);
      polyhedronOut[i] = (void*)P;
    }
  }

  *nConvex = convex_parts.size();

  return SUCCESS;
}

extern "C" void* pyg4_cgal_surfacemesh_union(void *mesh1In, 
					     void *mesh2In) 
{
  Surface_mesh *mesh1 = (Surface_mesh*)mesh1In;
  Surface_mesh *mesh2 = (Surface_mesh*)mesh2In;
  Surface_mesh *out   = new Surface_mesh();
  CGAL::Polygon_mesh_processing::corefine_and_compute_union(*mesh1,*mesh2,*out);
  return (void*)(out);
}

extern "C" void* pyg4_cgal_vertex_to_polygon(double **verticesIn, 
					     int nVertices, 
					     bool debugIo = false) 
{
  Polygon_2 *polygon = new Polygon_2();
  if(debugIo) {
    std::cout << "pyg4_cgal_vertex_to_polygon> polygon ptr " << polygon << std::endl;
    std::cout << "pyg4_cgal_vertex_to_polygon> nVertices=" << nVertices << std::endl;
  }
  for(int i=0;i<nVertices;++i) {
    if(debugIo) 
      std::cout << "pyg4_cgal_vertex_to_polygon> vertex " 
		<< verticesIn[i][0] << " " 
		<< verticesIn[i][1] << std::endl;
    polygon->push_back(Point_2(verticesIn[i][0], verticesIn[i][1]));
  }
  return (void*)polygon;
}

extern "C" int pyg4_cgal_polygon_to_vertex(void *polygonIn, double **vertices, int *nVerts) 
{
  Polygon_2 *polygon = (Polygon_2*)polygonIn;
  int i =0;
  for(auto p = polygon->vertices_begin(); p != polygon->vertices_end(); ++p) {
    vertices[i][0] = CGAL::to_double((*p).x());
    vertices[i][1] = CGAL::to_double((*p).y());

    //std::cout << CGAL::to_double((*p).x()) << std::endl;

    ++i;
  }

  *nVerts = polygon->size();

  return SUCCESS;  
}

extern "C" int pyg4_cgal_polygon_to_convexpolygons(void *polygonIn, 
						   void **polygonOut, 
						   int *nConvex) 
{

  Polygon_2 *polygon = (Polygon_2*)polygonIn;
  //  std::cout << "pyg4_cgal_polygon_to_convexpolygons> polygon ptr " << polygon  << std::endl;

  Polygon_list partition_polys;
  
  CGAL::optimal_convex_partition_2(polygon->vertices_begin(),
				   polygon->vertices_end(),
				   std::back_inserter(partition_polys));

  int i = 0;
  for(auto p = partition_polys.begin(); p != partition_polys.end(); ++p) {
    //    std::cout << "pyg4_cgal_polygon_to_convexpolygons> " << i << std::endl;
    polygonOut[i] = (void*)new Polygon_2(*p);
    i++;
  }

  *nConvex = partition_polys.size();
  
  return SUCCESS;  
}

extern "C" int pyg4_cgal_delete_polygon(void *polygonIn) 
{
  Polygon_2 *polygon = (Polygon_2*)polygonIn;
  delete polygon;

  return SUCCESS;
}

extern "C" int pyg4_cgal_delete_polygonlist(void *polygonListIn) 
{
  delete (Polygon_list*)polygonListIn;
  return SUCCESS;
}
