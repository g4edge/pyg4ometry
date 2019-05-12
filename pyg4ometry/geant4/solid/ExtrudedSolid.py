from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Polygon as _Polygon
import numpy as _np

import logging as _log

class ExtrudedSolid(_SolidBase):
    def __init__(self, name, pPolygon, pZslices, registry=None, lunit="mm"):
        """
        pPolygon: List of lists with the x-y coordinates of vertices for the polygon.
        pZslices: List of lists with z-coordinate of a slice, slice offsets in x-y and scaling

        Example: Triangular prism with 2 slices
        pPoligon = [[x1,y1],[x2,y2],[x3,v3]] - vertices of polygon in clockwise order
        zSlices  = [[z1,[offsx1, offsy1],scale1],[z2,[offsx2, offsy2],scale2]]
        """
        self.type     = 'ExtrudedSolid'
        self.name     = name

        self.pPolygon = pPolygon
        self.pZslices = pZslices 
        self.lunit    = lunit

        if registry :
            registry.addSolid(self)

    def __repr__(self):
        return "Extruded solid: {}".format(self.name)

    def polygon_area(self,vertices):
        # Using the shoelace formula
        xy = _np.array(vertices).T
        x = xy[0]
        y = xy[1]
        signed_area = 0.5*(_np.dot(x,_np.roll(y,1))-_np.dot(y,_np.roll(x,1)))
        return signed_area

    def pycsgmesh(self):
        _log.info('xtru.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        zpos     = [zslice[0].eval()*luval for zslice in self.pZslices]
        x_offs   = [zslice[1][0].eval()*luval for zslice in self.pZslices]
        y_offs   = [zslice[1][1].eval()*luval for zslice in self.pZslices]
        scale    = [zslice[2].eval() for zslice in self.pZslices]
        vertices = [[pPolygon[0].eval()*luval, pPolygon[1].eval()*luval] for pPolygon in self.pPolygon]
        nslices  = len(self.pZslices)

        _log.info('xtru.pycsgmesh> mesh')
        polygons  = []
        polygonsT = []
        polygonsB = []

        if self.polygon_area(vertices) < 0:
            vertices = list(reversed(vertices))


        poly_top = [_Vertex(_Vector(scale[-1]*vert[0]+x_offs[-1],
                                  scale[-1]*vert[1]+y_offs[-1],
                                  zpos[-1]),None) for vert in list(reversed(vertices))]


        poly_bot = [_Vertex(_Vector(scale[0]*vert[0]+x_offs[0],
                                  scale[0]*vert[1]+y_offs[0],
                                  zpos[0]),None) for vert in vertices]

        polygonsT.append(_Polygon(poly_top))
        polygonsB.append(_Polygon(poly_bot))

        # It appears we must append the top and bottom faces and then tile the sides
        polygons.extend(polygonsT)
        polygons.extend(polygonsB)

        maxn = len(vertices)

        for l in range(0, nslices-1):
            l_curr = l
            l_next = l + 1

            for n in range(maxn):
                n_next = (n+1) % maxn

                vert = vertices[nslices - n]
                vert_next = vertices[nslices - n - 1]

                poly = _Polygon([_Vertex(_Vector(scale[l_curr]*vert[0]+x_offs[l_curr],
                                                 scale[l_curr]*vert[1]+y_offs[l_curr],
                                                 zpos[l_curr]), None),

                                 _Vertex(_Vector(scale[l_curr]*vert_next[0]+x_offs[l_curr],
                                                 scale[l_curr]*vert_next[1]+y_offs[l_curr],
                                                 zpos[l_curr]), None),

                                 _Vertex(_Vector(scale[l_next]*vert_next[0]+x_offs[l_next],
                                                 scale[l_next]*vert_next[1]+y_offs[l_next],
                                                 zpos[l_next]), None),

                                 _Vertex(_Vector(scale[l_next]*vert[0]+x_offs[l_next],
                                                 scale[l_next]*vert[1]+y_offs[l_next],
                                                 zpos[l_next]), None)])

                polygons.append(poly)


        mesh = _CSG.fromPolygons(polygons)

        return mesh
