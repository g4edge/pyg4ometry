from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG
from pyg4ometry.pycsg.geom import Polygon as _Polygon
from pyg4ometry.pycsg.geom import Vertex as _Vertex
from pyg4ometry.pycsg.geom import Vector as _Vector

import logging as _log

class Trd(_SolidBase):
    """
    Constructs a trapezoid.

    Inputs:
        name:  string, name of the volume
        pDx1:  float, half-length along x at the surface positioned at -dz
        pDx2:  float, half-length along x at the surface postitioned at +dz
        pDy1:  float, half-length along y at the surface positioned at -dz
        pDy2:  float, half-length along y at the surface positioned at +dz
        dz:    float, half-length along the z axis
    """
    def __init__(self, name, pDx1, pDx2, pDy1, pDy2, pDz, registry=None):
        self.type   = 'Trd'
        self.name   = name
        self.pX1    = pDx1
        self.pX2    = pDx2
        self.pY1    = pDy1
        self.pY2    = pDy2
        self.pZ     = pDz
        self.mesh   = None
        self.dependents = []
        if registry:
            registry.addSolid(self)

    def pycsgmesh(self):
        _log.info('trd.pycsgmesh> antlr')
        pX1 = float(self.pX1)/2.
        pX2 = float(self.pX2)/2.
        pY1 = float(self.pY1)/2.
        pY2 = float(self.pY2)/2.
        pZ  = float(self.pZ)/2.

        _log.info('trd.pycsgmesh> mesh')
        mesh  = _CSG.fromPolygons([_Polygon([_Vertex(_Vector(-pX2,  pY2, pZ), None),
                                             _Vertex(_Vector(-pX2, -pY2, pZ), None),
                                             _Vertex(_Vector(pX2,  -pY2, pZ), None),
                                             _Vertex(_Vector(pX2,  pY2,  pZ), None)]),
                                   
                                   _Polygon([ _Vertex(_Vector(-pX1, -pY1, -pZ), None),
                                              _Vertex(_Vector(-pX1,  pY1, -pZ), None),
                                              _Vertex(_Vector(pX1,   pY1, -pZ), None),
                                              _Vertex(_Vector(pX1,  -pY1, -pZ), None)]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2,  -pY2,  pZ), None),
                                             _Vertex(_Vector(-pX2, -pY2,  pZ), None),
                                             _Vertex(_Vector(-pX1, -pY1, -pZ), None),
                                             _Vertex(_Vector(pX1,  -pY1, -pZ), None)]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2,  pY2,  pZ), None),
                                             _Vertex(_Vector(pX1,  pY1, -pZ), None),
                                             _Vertex(_Vector(-pX1, pY1, -pZ), None),
                                             _Vertex(_Vector(-pX2, pY2,  pZ), None)]),
                                   
                                   _Polygon([_Vertex(_Vector(-pX2,  pY2,  pZ), None),
                                             _Vertex(_Vector(-pX1,  pY1, -pZ), None),
                                             _Vertex(_Vector(-pX1, -pY1, -pZ), None),
                                             _Vertex(_Vector(-pX2, -pY2,  pZ), None)]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2, -pY2,  pZ), None),
                                             _Vertex(_Vector(pX1, -pY1, -pZ), None),
                                             _Vertex(_Vector(pX1,  pY1, -pZ), None),
                                             _Vertex(_Vector(pX2,  pY2,  pZ), None)])])
        
        return mesh

