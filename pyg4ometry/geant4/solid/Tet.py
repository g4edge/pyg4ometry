from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from Plane import Plane as _Plane
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np

from copy import deepcopy as _dc

class Tet(_SolidBase):
    def __init__(self, name, anchor, p2, p3, p4,
                 degeneracyFlag=False, register=True):
        """
        Constructs a tetrahedra.

        Inputs:
          name:           string, name of the volume
          anchor:         list, anchor point
          p2:             list, point 2
          p3:             list, point 3
          p4:             list, point 4
          degeneracyFlag: bool, indicates degeneracy of points
        """
        self.type    = 'Tet'
        self.name    = name
        self.anchor  = anchor
        self.p2      = p2
        self.p3      = p3
        self.p4      = p4
        self.degen   = degeneracyFlag
        if register:
            _registry.addSolid(self)


    def pycsgmesh(self):
        vert_ancr = _Vertex(_Vector(self.p4[0], self.p4[1], self.p4[2]), None)
        base      = [self.anchor, self.p2, self.p3]
        vert_base = []

        for i in range(len(base)):
            vert_base.append(_Vertex(_Vector(base[i][0],base[i][1],base[i][2]), None))
        self.mesh = _CSG.fromPolygons([_Polygon([_dc(vert_base[2]), _dc(vert_base[1]), _dc(vert_base[0])], None),
                                       _Polygon([_dc(vert_base[1]), _dc(vert_ancr), _dc(vert_base[0])], None),
                                       _Polygon([_dc(vert_base[2]), _dc(vert_ancr), _dc(vert_base[1])], None),
                                       _Polygon([_dc(vert_base[0]), _dc(vert_ancr), _dc(vert_base[2])], None)])

        return self.mesh
