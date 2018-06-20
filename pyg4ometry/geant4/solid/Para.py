from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np

import math as _math
from math import cos as _cos
from math import sin as _sin
from math import acos as _acos
from math import asin as _asin

class Para(_SolidBase):
    """
    Constructs a parallelepiped.

    Inputs:
    name:  string, name of the volume
    pX:    float, half-length along x
    pY:    float, half-length along y
    pZ:    float, half-length along z
    pAlpha: float, angle formed by the y axis and the plane joining the centres of the faces parallel tothe z-x plane at -dy and +dy
    pTheta: float, polar angle of the line joining the centres of the faces at -dz and +dz in z
    pPhi:   float, azimuthal angle of the line joining the centres of the faces at -dx and +dz in z
    """

    def __init__(self,name,pDx,pDy,pDz,pAlpha,pTheta,pPhi, register=True):


        self.type     = 'Para'
        self.name   = name
        self.pX     = pDx
        self.pY     = pDy
        self.pZ     = pDz
        self.pAlpha = pAlpha
        self.pTheta = pTheta
        self.pPhi   = pPhi
        self.dx_y   = self.pY*_sin(self.pAlpha)  #changes sign as the y component
        self.dx_z   = +self.pZ*_sin(self.pTheta) #changes sign as the z component
        self.dy     = self.pZ*_sin(self.pPhi)
        self.dz     = self.pZ-self.pZ*_cos(pPhi)
        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):
        self.mesh  = _CSG.fromPolygons([_Polygon([_Vertex(_Vector(-self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(-self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(-self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(-self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(-self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(-self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(-self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(-self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None)]),
                                        _Polygon([_Vertex(_Vector(self.pX-self.dx_y-self.dx_z,-self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y-self.dx_z, self.pY-self.dy,-self.pZ+self.dz), None),
                                                  _Vertex(_Vector(self.pX+self.dx_y+self.dx_z, self.pY+self.dy, self.pZ-self.dz), None),
                                                  _Vertex(_Vector(self.pX-self.dx_y+self.dx_z,-self.pY+self.dy, self.pZ-self.dz), None)])])


        return self.mesh
