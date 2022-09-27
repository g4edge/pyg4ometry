#include "algo.h"

#include <sstream>

namespace std
{
  inline void hash_combine(std::size_t) {}

  template <typename T, typename... Rest>
  inline void hash_combine(std::size_t &seed, const T &v, Rest... rest) {
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    std::hash_combine(seed, rest...);
  }

  template<> struct hash<Surface_mesh*> {
    std::size_t operator()(const Surface_mesh *sm) const {
      using std::size_t;
      using std::hash;

      std::size_t h = 0;

      // loop over vertices
      Surface_mesh::Point p;
      for(Surface_mesh::Vertex_index vd : sm->vertices()) {
        p = sm->point(vd);
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.x())));
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.y())));
        std::hash_combine(h,std::hash<double>()(CGAL::to_double(p.z())));
      }

      // loop over faces
      /*
      for(Surface_mesh::Face_index fd : sm->faces()) {
        for(Surface_mesh::Halfedge_index hd :  CGAL::halfedges_around_face(sm->halfedge(fd),*sm)) {
          // std::hash_combine(h,std::hash<int>()((int)sm->source(hd)));
        }
      }
      */

      return h;
    }
  };
}

/*********************************************
Polyhedron
*********************************************/
Polyhedron::Polyhedron() {
  _polyhedron = new Polyhedron_3();
}

Polyhedron::Polyhedron(const std::vector<std::vector<double>> &vertices,
		       const std::vector<std::vector<int>>    &facets)
{
  _polyhedron = new Polyhedron_3();
  Build_Polygon_VertexFacet<HalfedgeDS_3> pvf(vertices, facets);
  _polyhedron->delegate(pvf);
}


Polyhedron::Polyhedron(const py::list vertices,
		       const py::list facets) {

}

Polyhedron::Polyhedron(const py::array_t<double> vertices,
		       const py::array_t<int> facest) {

}

Polyhedron::~Polyhedron() {
  delete _polyhedron;
}


/*********************************************
Nef Polyhedron
*********************************************/
NefPolyhedron::NefPolyhedron() {
  _nef_polyhedron = new Nef_polyhedron_3();  
}

NefPolyhedron::NefPolyhedron(const Polyhedron &polyhedron) {
  _nef_polyhedron = new Nef_polyhedron_3(*polyhedron._polyhedron);
}

NefPolyhedron::NefPolyhedron(const SurfaceMesh &surfacemesh) {
  _nef_polyhedron = new Nef_polyhedron_3(*surfacemesh._surfacemesh);
}

NefPolyhedron::NefPolyhedron(Nef_polyhedron_3 *nef_polyhedron) {
  _nef_polyhedron = nef_polyhedron;
}

NefPolyhedron::~NefPolyhedron() {
  delete _nef_polyhedron;
}

std::vector<NefPolyhedron*> NefPolyhedron::convexDecomposition() {
  std::vector<NefPolyhedron*> decomposed; 

  py::print("starting decomposition");
  CGAL::convex_decomposition_3(*_nef_polyhedron);
  py::print("finished decomposition");

  Nef_polyhedron_3::Volume_const_iterator ci = ++(*_nef_polyhedron).volumes_begin();
  for(int i=0 ; ci != (*_nef_polyhedron).volumes_end(); ++ci, ++i) {    
    if(ci->mark()) {
      py::print("volume");
      Polyhedron P = Polyhedron();
      (*_nef_polyhedron).convert_inner_shell_to_polyhedron(ci->shells_begin(),*(P._polyhedron));
      decomposed.push_back(new NefPolyhedron(P));
    }
  }
  
  return decomposed;
}

void NefPolyhedron::print() {
  Nef_polyhedron_3::Volume_const_iterator vi = (*_nef_polyhedron).volumes_begin();
  for(int i=0 ; vi != (*_nef_polyhedron).volumes_end(); ++vi, ++i) {
    Nef_polyhedron_3::Shell_entry_const_iterator si = vi->shells_begin();
    py::print("volume",i);
    for(int j=0; si != vi->shells_end(); ++si, j++) {      
      py::print("volume",i,"shell",j);
    }    
  }  
}

int NefPolyhedron::number_of_volumes() {
  return _nef_polyhedron->number_of_volumes();
}

/*********************************************
Surface Mesh
*********************************************/
SurfaceMesh::SurfaceMesh() {
  _surfacemesh = new Surface_mesh();
}

SurfaceMesh::SurfaceMesh(const SurfaceMesh &mesh) {
  _surfacemesh = new Surface_mesh(*(mesh._surfacemesh));
}

SurfaceMesh::SurfaceMesh(Surface_mesh *mesh) {
  _surfacemesh = mesh;
}

SurfaceMesh::SurfaceMesh(py::list vertices,
			 py::list faces)    {
  _surfacemesh = new Surface_mesh();

  // loop over vertices
  for (py::handle vHandle : vertices) {
    py::list vList = vHandle.cast<py::list>();
    add_vertex(vList[0].cast<double>(),
	       vList[1].cast<double>(),
	       vList[2].cast<double>());
  }

  // loop over faces
  for (py::handle fHandle : faces) {
    py::list fList = fHandle.cast<py::list>();
    add_face(fList[0].cast<int>(),
	     fList[1].cast<int>(),
	     fList[2].cast<int>());
  }
}

SurfaceMesh::SurfaceMesh(py::array_t<double> vertices,
			 py::array_t<int>    faces)    {
  _surfacemesh = new Surface_mesh();

  // loop over vertices

  // loop over faces
}

SurfaceMesh::SurfaceMesh(std::string &fileName) {
  _surfacemesh = new Surface_mesh();
  std::ifstream ifstr(fileName);
  ifstr >> *_surfacemesh;
  ifstr.close();
}

SurfaceMesh::~SurfaceMesh() {
  delete _surfacemesh;
}

std::size_t SurfaceMesh::add_vertex(double x, double y, double z) {
  size_t ret = _surfacemesh->add_vertex(Point(x,y,z));

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::add_vertex",x,y,z);
  py::print("SurfaceMesh::add_vertex",ret);
  #endif

  return ret;
}

std::size_t SurfaceMesh::add_face(std::size_t i, std::size_t j, std::size_t k) {
  size_t ret = _surfacemesh->add_face(Surface_mesh::Vertex_index(i),
				      Surface_mesh::Vertex_index(j),
				      Surface_mesh::Vertex_index(k));

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::add_face (tri)",i,j,k);
  py::print("SurfaceMesh::add_face (tri)",ret);
  #endif
  return ret;
}

std::size_t SurfaceMesh::add_face(std::size_t i, std::size_t j, std::size_t k, std::size_t l) {
  size_t ret = _surfacemesh->add_face(Surface_mesh::Vertex_index(i),
				      Surface_mesh::Vertex_index(j),
				      Surface_mesh::Vertex_index(k),
				      Surface_mesh::Vertex_index(l));

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::add_face (quad)",i,j,k,l);
  py::print("SurfaceMesh::add_face (quad)",ret);
  #endif

  return ret;
}

std::size_t SurfaceMesh::add_face(const std::vector<unsigned int> &face) {

  std::vector<Surface_mesh::Vertex_index> faceV;
  for(auto i : face) {
    faceV.push_back(Surface_mesh::Vertex_index(i));
  }

  return _surfacemesh->add_face(faceV);
}

void SurfaceMesh::translate(double x, double y, double z) {

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::translate",x,y,z);
  #endif

  Aff_transformation_3 transl(CGAL::TRANSLATION, Vector_3(x, y, z));
  CGAL::Polygon_mesh_processing::transform(transl,*_surfacemesh);
}

void SurfaceMesh::transform(double m11, double m12, double m13,
			    double m21, double m22, double m23,
			    double m31, double m32, double m33) {
  Aff_transformation_3 tform(m11,m12,m13,
			     m21,m22,m23,
			     m31,m32,m33,1);
  CGAL::Polygon_mesh_processing::transform(tform,*_surfacemesh);
}

SurfaceMesh* SurfaceMesh::unioN(SurfaceMesh &mesh2) {
  Surface_mesh *out = new Surface_mesh();

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::unioN",(void*)_surfacemesh,(void*)mesh2._surfacemesh,(void*)out);
  #endif

  /*bool valid_union = */CGAL::Polygon_mesh_processing::corefine_and_compute_union(*_surfacemesh,*(mesh2._surfacemesh), *out);
  return new SurfaceMesh(out);
}

SurfaceMesh* SurfaceMesh::intersect(SurfaceMesh &mesh2) {
  Surface_mesh *out = new Surface_mesh();

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::intersect",(void*)_surfacemesh,(void*)mesh2._surfacemesh,(void*)out);
  #endif

  /*bool valid_intersection = */CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(*_surfacemesh,*(mesh2._surfacemesh), *out);
  return new SurfaceMesh(out);
}

SurfaceMesh* SurfaceMesh::subtract(SurfaceMesh &mesh2) {
  Surface_mesh *out = new Surface_mesh();

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::intersect",(void*)_surfacemesh,(void*)mesh2._surfacemesh,(void*)out);
  #endif

  /*bool valid_difference = */CGAL::Polygon_mesh_processing::corefine_and_compute_difference(*_surfacemesh,*(mesh2._surfacemesh), *out);
  return new SurfaceMesh(out);
}

void SurfaceMesh::reverse_face_orientations() {

  #ifdef __DEBUG_PYIO__
  py::print("SurfaceMesh::reverse_face_orientations");
  #endif

  CGAL::Polygon_mesh_processing::reverse_face_orientations(*_surfacemesh);
}

bool SurfaceMesh::is_valid() {
  return _surfacemesh->is_valid(true);
}

bool SurfaceMesh::is_closed() {
  return CGAL::is_closed(*_surfacemesh);
}

bool SurfaceMesh::is_outward_oriented() {
  return CGAL::Polygon_mesh_processing::is_outward_oriented(*_surfacemesh);
}

bool SurfaceMesh::does_self_intersect() {
  return CGAL::Polygon_mesh_processing::does_self_intersect(*_surfacemesh);
}

bool SurfaceMesh::does_bound_a_volume() {
  return CGAL::Polygon_mesh_processing::does_bound_a_volume(*_surfacemesh);
}

void SurfaceMesh::triangulate_faces() {
  CGAL::Polygon_mesh_processing::triangulate_faces(*_surfacemesh);
}

void SurfaceMesh::isotropic_remeshing() {

  struct halfedge2edge
  {
    halfedge2edge(const Surface_mesh& m, std::vector<edge_descriptor>& edges) : m_mesh(m), m_edges(edges) {}
    void operator()(const halfedge_descriptor& h) const
    {
      m_edges.push_back(edge(h, m_mesh));
    }
    const Surface_mesh& m_mesh;
    std::vector<edge_descriptor>& m_edges;
  };

  std::vector<edge_descriptor> border;

  //CGAL::Polygon_mesh_processing::border_halfedges(_surfacemesh->faces(),*_surfacemesh,
  //                                                boost::make_function_output_iterator(halfedge2edge(*_surfacemesh, border)));

  //CGAL::Polygon_mesh_processing::split_long_edges(_surfacemesh->edges(), 0., *_surfacemesh);
  //CGAL::Polygon_mesh_processing::split_long_edges(_surfacemesh->edges(), 0.04, *_surfacemesh);
  //CGAL::Polygon_mesh_processing::split_long_edges(_surfacemesh->edges(), 0.03, *_surfacemesh);

  //std::cout << border.size() << std::endl;
  CGAL::Polygon_mesh_processing::isotropic_remeshing(_surfacemesh->faces(),0.1,*_surfacemesh,CGAL::Polygon_mesh_processing::parameters::number_of_iterations(3));
}

int SurfaceMesh::number_of_border_halfedges(bool verbose) {

  int ihole = 0;
  for(auto hei : halfedges(*_surfacemesh))
    {
      if(_surfacemesh->is_border(hei)) {
        ihole++;
        if(verbose)
	      py::print(int(hei),"hole");
        }
    }
  return ihole;
}

py::list* SurfaceMesh::toVerticesAndPolygons() {
  py::list *verts = new py::list();
  py::list *polys = new py::list();

  //std::vector<std::vector<double>> verts;
  //std::vector<std::vector<int>>    polys;

  Surface_mesh::Point p;
  for(Surface_mesh::Vertex_index vd : _surfacemesh->vertices()) {
    py::list *v = new py::list();
    p = _surfacemesh->point(vd);
    v->append(CGAL::to_double(p.x()));
    v->append(CGAL::to_double(p.y()));
    v->append(CGAL::to_double(p.z()));
    verts->append(v);
  }

  int iCount = 0;
  for(Surface_mesh::Face_index fd : _surfacemesh->faces()) {
    py::list *p = new py::list();
    for(Surface_mesh::Halfedge_index hd :  CGAL::halfedges_around_face(_surfacemesh->halfedge(fd),*_surfacemesh)) {
      p->append((int)_surfacemesh->source(hd));
    }
    polys->append(p);
    ++iCount;
  }

  py::list *ret = new py::list();
  ret->append(verts);
  ret->append(polys);
  ret->append(iCount);

  return ret;
}

int SurfaceMesh::number_of_faces() {
  return _surfacemesh->number_of_faces();
}

int SurfaceMesh::number_of_vertices() {
  return _surfacemesh->number_of_vertices();
}

std::size_t SurfaceMesh::hash() {
  return std::hash<Surface_mesh*>{}(_surfacemesh);
}

std::string SurfaceMesh::toString() {
  std::ostringstream sstream;
  sstream << *_surfacemesh;
  return sstream.str();
}

/*********************************************
Haussdorf
*********************************************/

double haussdorf_distance(SurfaceMesh &m1, SurfaceMesh &m2) {
  auto s1 = m1._surfacemesh;
  auto s2 = m2._surfacemesh;
  return CGAL::Polygon_mesh_processing::approximate_Hausdorff_distance<
      CGAL::Sequential_tag>(
      *s1, *s2, CGAL::Polygon_mesh_processing::parameters::all_default(),
      CGAL::Polygon_mesh_processing::parameters::all_default());
}

double symmetric_haussdorf_distance(SurfaceMesh &m1, SurfaceMesh &m2) {
  auto s1 = m1._surfacemesh;
  auto s2 = m2._surfacemesh;
  return CGAL::Polygon_mesh_processing::
      approximate_symmetric_Hausdorff_distance<CGAL::Sequential_tag>(
          *s1, *s2, CGAL::Polygon_mesh_processing::parameters::all_default(),
          CGAL::Polygon_mesh_processing::parameters::all_default());
}

/*********************************************
Polygon2
*********************************************/
Polygon2::Polygon2() {
  _polygon = new Polygon_2();
};

Polygon2::Polygon2(const Polygon2 &poly) {
  _polygon = new Polygon_2(*(poly._polygon));
}

Polygon2::Polygon2(const Polygon_2 &poly) {
  _polygon = new Polygon_2(poly);
}

Polygon2::Polygon2(py::list &p) {
  _polygon = new Polygon_2();
  for (py::handle pHandle : p) {
    py::list pList = pHandle.cast<py::list>();
    push_back(pList[0].cast<double>(), pList[1].cast<double>());
  }
}

Polygon2::Polygon2(py::list &x, py::list &y) {
  _polygon = new Polygon_2();

  int i = 0;
  for (py::handle pHandle : x) {
    push_back(pHandle.cast<double>(), y[i].cast<double>());
    i++;
  }
}

Polygon2::Polygon2(py::array_t<double> &array) {
  _polygon = new Polygon_2();

  py::buffer_info buf = array.request();

  if (buf.ndim != 2)
    throw std::runtime_error("numpy.ndarray dims must be 2");

  double *ptr = (double*)buf.ptr;
  int n1 = buf.shape[0];
  int n2 = buf.shape[1];

  for(int i = 0; i< n1; i++) {
    push_back(ptr[i*n2+0],ptr[i*n2+1]);
  }
}

Polygon2::Polygon2(py::array_t<double> &array_x,
		   py::array_t<double> &array_y) {
  _polygon = new Polygon_2();

  py::buffer_info buf_x = array_x.request();
  py::buffer_info buf_y = array_y.request();

  if (buf_x.shape[0] != buf_y.shape[0])
    throw std::runtime_error("numpy.ndarray arrays need to be same length");

  int n = buf_x.shape[0];

  double *ptr_x = (double*)buf_x.ptr;
  double *ptr_y = (double*)buf_y.ptr;

  for(int i = 0; i< n; i++) {
    push_back(ptr_x[i],ptr_y[i]);
  }
}

Polygon2::~Polygon2() {
  delete _polygon;
};

void Polygon2::push_back(double x , double y) {
  _polygon->push_back(Point_2(x,y));
}

void Polygon2::push_back(py::list &list) {
  double x = list[0].cast<double>();
  double y = list[1].cast<double>();
  push_back(x,y);
}

void Polygon2::push_back(py::array_t<double> &array) {
  py::buffer_info buf = array.request();
  double* ptr = (double*)buf.ptr;
  double x = ptr[0];
  double y = ptr[1];
  push_back(x,y);
}

std::size_t Polygon2::size() const {
  return _polygon->size();
}

std::string Polygon2::toString() const {
  std::ostringstream sstream;
  sstream << "Polygon2[" << std::endl;
  for(auto vi = _polygon->vertices_begin(); vi != _polygon->vertices_end(); ++vi) {
    sstream << *vi << std::endl;
  }
  sstream << "]";
  return sstream.str();
}

void Polygon2::clear() {
  _polygon->clear();
}

void Polygon2::reverse_orientation() {
  _polygon->reverse_orientation();
}


bool Polygon2::is_simple() const {
  return _polygon->is_simple();
}

bool Polygon2::is_convex() const {
  return _polygon->is_convex();
}

int Polygon2::orientation() const {
  return _polygon->orientation();
}

std::list<Polygon2> Polygon2::optimal_convex_partition() {
  std::list<Polygon_2> partition_polys_temp;
  std::list<Polygon2>  partition_polys;

  // CW or CCW
  if(orientation() != 1) {
    reverse_orientation();
  }

  CGAL::optimal_convex_partition_2(_polygon->vertices_begin(),
				   _polygon->vertices_end(),
				   std::back_inserter(partition_polys_temp));

  for(auto p : partition_polys_temp) {
    partition_polys.push_back(Polygon2(p));
  }

  return partition_polys;
}

/*********************************************
PYBIND
*********************************************/
PYBIND11_MODULE(algo, m) {

  py::class_<Polyhedron>(m,"Polyhedron")
    .def(py::init<>());

  py::class_<SurfaceMesh>(m,"SurfaceMesh")
    .def(py::init<>())
    .def(py::init<py::list &, py::list &>())
    .def(py::init<std::string &>())
    .def("add_vertex",&SurfaceMesh::add_vertex)
    .def("add_face",(std::size_t (SurfaceMesh::*)(std::size_t, std::size_t, std::size_t)) &SurfaceMesh::add_face)
    .def("add_face",(std::size_t (SurfaceMesh::*)(std::size_t, std::size_t, std::size_t, std::size_t)) &SurfaceMesh::add_face)
    .def("translate",&SurfaceMesh::translate)
    .def("transform",&SurfaceMesh::transform)
    .def("union",&SurfaceMesh::unioN)
    .def("intersect",&SurfaceMesh::intersect)
    .def("subtract",&SurfaceMesh::subtract)
    .def("is_valid",&SurfaceMesh::is_valid)
    .def("is_closed",&SurfaceMesh::is_closed)
    .def("is_outward_oriented",&SurfaceMesh::is_outward_oriented)
    .def("does_self_intersect",&SurfaceMesh::does_self_intersect)
    .def("does_bound_a_volume",&SurfaceMesh::does_bound_a_volume)
    .def("number_of_border_halfedges",&SurfaceMesh::number_of_border_halfedges,"number of border halfedges ", py::arg("verbose") = false)
    .def("triangulate_faces",&SurfaceMesh::triangulate_faces)
    .def("isotropic_remeshing",&SurfaceMesh::isotropic_remeshing)
    .def("toVerticesAndPolygons",&SurfaceMesh::toVerticesAndPolygons)
    .def("number_of_faces",&SurfaceMesh::number_of_faces)
    .def("number_of_vertices",&SurfaceMesh::number_of_vertices)
    .def("__repr__",&SurfaceMesh::toString);

  m.def("haussdorf_distance", &haussdorf_distance);
  m.def("symmetric_haussdorf_distance", &symmetric_haussdorf_distance);

  py::class_<NefPolyhedron>(m,"NefPolyhedron")
    .def(py::init<>())
    .def(py::init<const Polyhedron &>())
    .def(py::init<const SurfaceMesh &>())
    .def("convexDecomposition",&NefPolyhedron::convexDecomposition)  
    .def("print",&NefPolyhedron::print)
    .def("number_of_volumes",&NefPolyhedron::number_of_volumes);

  py::class_<Polygon2>(m,"Polygon2")
    .def(py::init<>())
    .def(py::init<py::list &>())
    .def(py::init<py::list &, py::list &>())
    .def(py::init<py::array_t<double> &>())
    .def(py::init<py::array_t<double> &, py::array_t<double> &>())
    .def("push_back",(void (Polygon2::*)(double, double)) &Polygon2::push_back)
    .def("push_back",(void (Polygon2::*)(py::list &)) &Polygon2::push_back)
    .def("push_back",(void (Polygon2::*)(py::array_t<double> &)) &Polygon2::push_back)
    .def("__repr__",&Polygon2::toString)
    .def("__len__",&Polygon2::size)
    .def("clear",&Polygon2::clear)
    .def("reverse_orientation",&Polygon2::reverse_orientation)
    .def("is_simple",&Polygon2::is_simple)
    .def("is_convex",&Polygon2::is_convex)
    .def("orientation",&Polygon2::orientation)
    .def("optimal_convex_partition",&Polygon2::optimal_convex_partition);

}
