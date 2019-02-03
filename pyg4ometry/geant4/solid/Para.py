from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from pyg4ometry.geant4.Registry import registry as _registry
from pyg4ometry.pycsg.core import CSG as _CSG
from pyg4ometry.pycsg.geom import Vector as _Vector
from pyg4ometry.pycsg.geom import Vertex as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon

import numpy as _np
import math as _math

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

    def __init__(self,name,pDx,pDy,pDz,pAlpha,pTheta,pPhi, registry=None):
        import pyg4ometry.gdml.Defines as _Defines

        self.type     = 'Para'
        self.name   = name
        self.pX     = pDx
        self.pY     = pDy
        self.pZ     = pDz
        self.pAlpha = pAlpha
        self.pTheta = pTheta
        self.pPhi   = pPhi
        if registry:
            registry.addSolid(self)

    def pycsgmesh(self):

        pX     = float(self.pX) 
        pY     = float(self.pY)
        pZ     = float(self.pZ)
        pAlpha = float(self.pAlpha)
        pTheta = float(self.pTheta)
        pPhi   = float(self.pPhi)
        
        dx_y   = pY*_math.sin(pAlpha)  #changes sign as the y component
        dx_z   = pZ*_math.sin(pTheta)  #changes sign as the z component
        dy     = pZ*_math.sin(pPhi)
        dz     = pZ-pZ*_math.cos(pPhi)        
                        
        mesh  = _CSG.fromPolygons([_Polygon([_Vertex(_Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX+dx_y-dx_z, pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX-dx_y-dx_z,-pY-dy,-pZ+dz), None)]),
                                        _Polygon([_Vertex(_Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(pX-dx_y+dx_z,-pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(pX+dx_y+dx_z, pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), None)]),
                                        _Polygon([_Vertex(_Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX-dx_y-dx_z,-pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX-dx_y+dx_z,-pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), None)]),
                                        _Polygon([_Vertex(_Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(pX+dx_y+dx_z, pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(pX+dx_y-dx_z, pY-dy,-pZ+dz), None)]),
                                        _Polygon([_Vertex(_Vector(-pX-dx_y-dx_z,-pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(-pX-dx_y+dx_z,-pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(-pX+dx_y+dx_z, pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(-pX+dx_y-dx_z, pY-dy,-pZ+dz), None)]),
                                        _Polygon([_Vertex(_Vector(pX-dx_y-dx_z,-pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX+dx_y-dx_z, pY-dy,-pZ+dz), None),
                                                  _Vertex(_Vector(pX+dx_y+dx_z, pY+dy, pZ-dz), None),
                                                  _Vertex(_Vector(pX-dx_y+dx_z,-pY+dy, pZ-dz), None)])])


        return mesh
