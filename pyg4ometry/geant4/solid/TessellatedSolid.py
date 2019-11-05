from SolidBase import SolidBase as _SolidBase
from Plane import Plane as _Plane
from pyg4ometry.geant4.Registry import registry as _registry
from pyg4ometry.pycsg.core import CSG     as _CSG
from pyg4ometry.pycsg.geom import Vector  as _Vector
from pyg4ometry.pycsg.geom import Vertex  as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon

import numpy as _np


    
class TessellatedSolid(_SolidBase):
    """
    Constructs a tessellated solid
    
    :param name:     of solid
    :type name:      str
    :param mesh:     mesh 
    :type mesh:      Freecad, Gdml or Stl
    :param registry: for storing solid
    :type registry:  Registry
    :param meshtype: type of mesh
    :type meshtype:  MeshType.Freecad
    
    """


    class MeshType : 
        Freecad = 1
        Gdml    = 2
        Stl     = 3

    def __init__(self, name, mesh, registry, meshtype=MeshType.Freecad, addRegistry=True):
        self.type        = 'TessellatedSolid'
        self.name        = name

        self.mesh        = mesh
        self.meshtype    = meshtype

        self.dependents = []

        #self.indexed_facet_list = []
        #self.unique_vertices    = []
        #self.reduceVertices()

        if addRegistry:
            registry.addSolid(self)
        self.registry = registry

    def __repr__(self):
        return self.type
    
    def pycsgmesh(self) :

        #############################################
        # render GDML mesh
        #############################################
        if self.meshtype == self.MeshType.Gdml :
            # vertex name - integer dict 
            vdict = {}
 
            i = 0
            for f in self.mesh :                 
                for j in range(0,3,1) :
                    try :
                        vdict[f[j]] 
                    except KeyError :
                        vdict[f[j]] = i 
                        i += 1
                        
            verts = [0 for dummy in range(0,len(vdict.keys()),1)] 
            facet = []
            for vdi in vdict.items(): 
                p = self.registry.defineDict[vdi[0]]
                verts[vdi[1]] = p.eval() 

            for f in self.mesh : 
                facet.append([vdict[f[0]],vdict[f[1]],vdict[f[2]]])

        #############################################
        # Mesh from CAD
        #############################################
        elif self.meshtype == self.MeshType.Freecad : 
            verts = self.mesh[0]
            facet = self.mesh[1]

        #############################################
        # Mesh from STL
        #############################################
        elif self.meshtype == self.MeshType.Stl : 
            verts = []
            facet = []
            
            i = 0 
            for f in self.mesh : 
                v1 = f[0][0]
                v2 = f[0][1]
                v3 = f[0][2]
                
                verts.append(v1)
                verts.append(v2)
                verts.append(v3)
                
                facet.append((3*i+0,3*i+1,3*i+2))
                i += 1

        else:
            raise ValueError("Urecognised mesh type: {}".format(self.meshtype))

        #############################################
        # Convert verts and facets to polygons 
        #############################################
        polygon_list = []

        for f in facet:
            #v1 = _Vertex(verts[f[0]])
            #v2 = _Vertex(verts[f[1]])
            #v3 = _Vertex(verts[f[2]])

            #polygon = _Polygon([v1,v2,v3])

            # This allows for both triangular and quadrilateral facets
            polygon = _Polygon([_Vertex(verts[facet_vertex]) for facet_vertex in f])
            polygon_list.append(polygon)            
        
        return _CSG.fromPolygons(polygon_list)        

