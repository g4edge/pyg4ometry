from SolidBase import SolidBase as _SolidBase
from Plane import Plane as _Plane
from pyg4ometry.geant4.Registry import registry as _registry
from pyg4ometry.pycsg.core import CSG     as _CSG
from pyg4ometry.pycsg.geom import Vector  as _Vector
from pyg4ometry.pycsg.geom import Vertex  as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon

import numpy as _np

class TessellatedSolid(_SolidBase):
    def __init__(self, name, facet_list, registry=None):
        """
        Constructs a tessellated solid

        Inputs:
          name:       string, name of the volume
          facet_list: lsit of 2-tuples (triangular facets) made up
                      of 1 3-tuple of 3-tuples (xyz vertices) and a 3-tuple normal

        Note: the normal is currently ingored as the vertex ordering is sufficient
        Example facet_list = [(((1,1,2),(2,1,3),(3,2,1)), (1,1,1)), ......]
        """
        self.type        = 'TesselatedSolid'
        self.name        = name

        self.facet_list  = facet_list

        # if self.facet_list is strings then don't do anything, if floats then need to add to defines 
        


        '''
        self.indexed_facet_list = []
        self.unique_vertices    = []
        self.reduceVertices()
        '''

        self.mesh              = None
        if registry:
            registry.addSolid(self)
            self.registry = registry

    def __repr__(self):
        return self.type

    def pycsgmesh(self) :
        
        # loop over facet list and make vectors of verticies 
        if isinstance(self.facet_list[0][0],str) :       
            # print 'positions'
            polygon_list = [] 
            for facet in self.facet_list :  
                vertex_list = []
                for vertex in facet :
                    v = self.registry.defineDict[vertex].eval()
                    vertex_list.append(_Vertex(v))
                polygon = _Polygon(vertex_list)
                polygon_list.append(polygon)

            return _CSG.fromPolygons(polygon_list)
        elif isinstance(self.facet_list[0][0][0][0],float) :
            # print 'floats'
            polygon_list = [] 
            for facet in self.facet_list : 
                vertex_list = [] 
                v1 = _Vertex(facet[0][0])
                v2 = _Vertex(facet[0][1])
                v3 = _Vertex(facet[0][2])
                polygon = _Polygon([v1,v2,v3])
                polygon_list.append(polygon)
                
            return _CSG.fromPolygons(polygon_list)            

    '''
    def reduceVertices(self):
        count_orig=0
        count_redu=0

        #Avoid continuously evaluating funciton references in loop
        unique_index = self.unique_vertices.index
        unique_append  = self.unique_vertices.append

        print "Compressing Tesselated solid vertices..."
        for facet in self.facet_list:
            normal = None #This is redundant
            vhashes = []
            for vertex in facet[0]:
                count_orig += 1
                try: #Avoid multiple O(n) 'x in y' operations with a try block
                    vert_idx = unique_index(vertex)
                except ValueError:
                    count_redu +=1
                    unique_append(vertex)
                    vert_idx = len(self.unique_vertices) - 1

                vhashes.append(vert_idx)
            self.indexed_facet_list.append([vhashes, normal])

        print "Total vertices: ", count_orig," , Unique vertices: ", count_redu
    def pycsgmesh(self):

#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self):
        def xyz2Vertex(xyztup, normal):
            return _Vertex(_Vector(xyztup), None)

        polygons = []
        for facet in self.indexed_facet_list:
            v1 = xyz2Vertex(self.unique_vertices[facet[0][0]], facet[1]) #Keep it simple
            v2 = xyz2Vertex(self.unique_vertices[facet[0][1]], facet[1])
            v3 = xyz2Vertex(self.unique_vertices[facet[0][2]], facet[1])
            polygons.append(_Polygon([v1, v2, v3]))

        self.mesh  = _CSG.fromPolygons(polygons)
        return self.mesh

    def csgmesh(self):
        pass
        '''
