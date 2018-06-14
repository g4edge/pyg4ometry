from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np

class Orb(_SolidBase):
    def __init__(self, name, pRMax, register=True):

        """
        Constructs a solid sphere.

        Inputs:
           name:     string, name of the volume
           pRMax:    float, outer radius
        """
        self.type = 'Orb'
        self.name = name
        self.pRMax = pRMax
        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):
        self.mesh = _CSG.sphere(center=[0,0,0], radius=self.pRMax)
        return self.mesh
