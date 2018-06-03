from SolidBase import SolidBase as _SolidBase
from Plane import Plane as _Plane
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np

class TesselatedSolid(_SolidBase) :
    def __init__(self, name, facet_list) :
        """
        Constructs an ellipsoid optinoally cut by planes perpendicular to the z-axis.

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
        self.mesh        = None
        _registry.addSolid(self)

    def __repr__(self):
        return self.type

    def pycsgmesh(self):

#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self) :
        def xyz2Vertex(xyztup, normal):
            return _Vertex(_Vector(xyztup), None)

        polygons = []
        for facet in self.facet_list:
            v1 = xyz2Vertex(facet[0][0], facet[1]) #Keep it simple
            v2 = xyz2Vertex(facet[0][1], facet[1])
            v3 = xyz2Vertex(facet[0][2], facet[1])
            polygons.append(_Polygon([v1, v2, v3]))

        self.mesh  = _CSG.fromPolygons(polygons)
        return self.mesh

    def csgmesh(self):
        pass
