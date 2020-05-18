from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

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

    def __init__(self, name, meshTess, registry, meshtype=MeshType.Freecad, addRegistry=True):
        self.type        = 'TessellatedSolid'
        self.name        = name

        self.meshtess    = meshTess
        self.meshtype    = meshtype

        self.dependents = []
        self.varNames = []

        if addRegistry:
            registry.addSolid(self)
        self.registry = registry

        if self.type == TessellatedSolid.MeshType.Gdml:
            # In GDML, vertices are defines that are referred to by name.
            # When merging registries, the vertx defines need to be carried over
            for f in self.meshtess:
                for facet_vertex in f:
                    if facet_vertex not in self.varNames:
                        self.varNames.append(facet_vertex)


    def __repr__(self):
        return self.type
    
    def mesh(self) :

        #############################################
        # render GDML mesh
        #############################################
        if self.meshtype == self.MeshType.Gdml :
            # vertex name - integer dict
            vdict = {}
 
            i = 0
            for f in self.meshtess:
                for facet_vertex in f:
                    try:
                        vdict[facet_vertex]
                    except KeyError:
                        vdict[facet_vertex] = i
                        i += 1
                        
            verts = [0 for dummy in range(0,len(vdict.keys()),1)] 
            facet = []
            for vdi in vdict.items(): 
                p = self.registry.defineDict[vdi[0]]
                verts[vdi[1]] = p.eval() 

            for f in self.meshtess:
                facet.append([vdict[fi] for fi in f])

        #############################################
        # Mesh from CAD
        #############################################
        elif self.meshtype == self.MeshType.Freecad : 
            verts = self.meshtess[0]
            facet = self.meshtess[1]

        #############################################
        # Mesh from STL
        #############################################
        elif self.meshtype == self.MeshType.Stl : 
            verts = []
            facet = []
            
            i = 0 
            for f in self.meshtess :
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
            # This allows for both triangular and quadrilateral facets
            polygon = _Polygon([_Vertex(verts[facet_vertex]) for facet_vertex in f])
            polygon_list.append(polygon)            
        
        return _CSG.fromPolygons(polygon_list)        

