from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
import numpy as _np

class Orb(_SolidBase):
    def __init__(self, name, pRMax):

        """
        Constructs a solid sphere. 
    
        Inputs:
           name:     string, name of the volume
           pRMax:    float, outer radius
        """   
        self.type = 'Orb'
        self.name = name
        self.pRMax = pRMax
        _registry.addSolid(self)

    def pycsgmesh(self):
        self.mesh = _CSG.sphere(center=[0,0,0], radius=self.pRMax)
        return self.mesh
