from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Polygon as _Polygon
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector

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
    def __init__(self, name, pDx1, pDx2, pDy1, pDy2, pDz, register=True):
        self.type   = 'Trd'
        self.name   = name
        self.pX1    = pDx1
        self.pX2    = pDx2
        self.pY1    = pDy1
        self.pY2    = pDy2
        self.pZ     = pDz
        self.mesh   = None
        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):
#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self):
        self.mesh  = _CSG.fromPolygons([_Polygon([_Vertex(_Vector(-self.pX1,-self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(-self.pX1, self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX1, self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX1,-self.pY1,-self.pZ), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX2,-self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(self.pX2,-self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(self.pX2, self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(-self.pX2, self.pY2, self.pZ), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX1,-self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX1,-self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX2,-self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(-self.pX2,-self.pY2, self.pZ), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX1, self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(-self.pX2, self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(self.pX2, self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(self.pX1, self.pY1,-self.pZ), None)]),
                                        _Polygon([_Vertex(_Vector(-self.pX1,-self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(-self.pX2,-self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(-self.pX2, self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(-self.pX1, self.pY1,-self.pZ), None)]),
                                        _Polygon([_Vertex(_Vector(self.pX1,-self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX1, self.pY1,-self.pZ), None),
                                                  _Vertex(_Vector(self.pX2, self.pY2, self.pZ), None),
                                                  _Vertex(_Vector(self.pX2,-self.pY2, self.pZ), None)])])

        return self.mesh

    def csgmesh(self):
        return self.mesh
