from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Polygon as _Polygon
import numpy as _np

class ExtrudedSolid(_SolidBase):
    def __init__(self, name, pPolygon, pZslices, register=True):
        """
        pPoligon: List of lists with the x-y coordinates of vertices for the polygon.
        pZslices: List of lists with z-coordinate of a slice, slice offsets in x-y and scaling

        Example: Triangular prism with 2 slices
        pPoligon = [[x1,y1],[x2,y2],[x3,v3]] - vertices of polygon in clockwise order
        zSlices  = [[z1,[offsx1, offsy1],scale1],[z2,[offsx2, offsy2],scale2]]
        """
        self.type     = 'ExtrudedSolid'
        self.name     = name
        self.zpos     = [zslice[0] for zslice in pZslices]
        self.x_offs   = [zslice[1][0] for zslice in pZslices]
        self.y_offs   = [zslice[1][1] for zslice in pZslices]
        self.scale    = [zslice[2] for zslice in pZslices]
        self.vertices = pPolygon
        self.nslices  = len(pZslices)
        self.mesh = None
        if register:
            _registry.addSolid(self)

    def __repr__(self):
        return "Extruded solid:" + str(self.name)

    def pycsgmesh(self):

#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self):
        polygons  = []
        polygonsT = []
        polygonsB = []

        polygonsT.append(_Polygon([_Vertex(_Vector(self.scale[-1]*vert[0]+self.x_offs[-1],
                                                   self.scale[-1]*vert[1]+self.y_offs[-1],
                                                   self.zpos[-1]),None) for vert in self.vertices]))

        polygonsB.append(_Polygon([_Vertex(_Vector(self.scale[0]*vert[0]+self.x_offs[0],
                                                   self.scale[0]*vert[1]+self.y_offs[0],
                                                   self.zpos[0]),None) for vert in  list(reversed(self.vertices))]))

        polygons.extend(polygonsB)

        maxn = len(self.vertices)

        for l in range(0, self.nslices):
            for n in range(maxn):
                n_next = (n+1) % maxn

                if l < self.nslices - 1:
                    vert = self.vertices[n]
                    vert_next = self.vertices[n_next]
                else:
                    vert = self.vertices[self.nslices - n]
                    vert_next = self.vertices[self.nslices - n - 1]

                poly = _Polygon([_Vertex(_Vector(self.scale[l]*vert[0]+self.x_offs[l],
                                                 self.scale[l]*vert[1]+self.y_offs[l],
                                                 self.zpos[l]), None),

                                 _Vertex(_Vector(self.scale[l]*vert_next[0]+self.x_offs[l],
                                                 self.scale[l]*vert_next[1]+self.y_offs[l],
                                                 self.zpos[l]), None),

                                 _Vertex(_Vector(self.scale[l-1]*vert_next[0]+self.x_offs[l-1],
                                                 self.scale[l-1]*vert_next[1]+self.y_offs[l-1],
                                                 self.zpos[l-1]), None),

                                 _Vertex(_Vector(self.scale[l-1]*vert[0]+self.x_offs[l-1],
                                                 self.scale[l-1]*vert[1]+self.y_offs[l-1],
                                                 self.zpos[l-1]), None)])
                polygons.append(poly)

        polygons.extend(polygonsT)

        self.mesh = _CSG.fromPolygons(polygons)

        return self.mesh

    def csgmesh(self):
        return self.mesh
