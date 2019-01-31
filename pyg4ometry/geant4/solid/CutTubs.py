from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from Tubs import Tubs as _Tubs
from Plane import Plane as _Plane

import numpy as _np

class CutTubs(_SolidBase):
    """
    Constructs a cylindrical section with cuts.

    Inputs:
        name:      string, name of the volume
        pRMin:     float, inner radius
        pRMax:     float, outer radius
        pDz:       float, half-length along z
        pSPhi:     float, starting phi angle
        pDPhi:     float, angle of segment in radians
        pLowNorm:  list,  normal vector of the cut plane at -pDz
        pHighNorm: list, normal vector of the cut plane at +pDz
    """
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi,
                 pLowNorm, pHighNorm, registry=None):
        self.type      = 'CutTubs'
        self.name      = name
        self.pRMin     = pRMin
        self.pRMax     = pRMax
        self.pDz       = pDz
        self.pSPhi     = pSPhi
        self.pDPhi     = pDPhi
        self.pLowNorm  = pLowNorm
        self.pHighNorm = pHighNorm
        self.mesh      = None
        if registry:
            registry.addSolid(self)
            self.registry = registry

    def __repr__(self):
        return 'Cut tubs :{}'.format(self.name)

    def pycsgmesh(self):
        self.basicmesh()
        if self.pLowNorm != [0,0,-1] or self.pHighNorm != [0,0,1]:
            self.csgmesh()

        return self.mesh

    def basicmesh(self):
        pRMin = float(self.pRMin)
        pRMax = float(self.pRMax)
        pDz   = float(self.pDz)
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)

        self.mesh = _Tubs("tubs_temp", self.pRMin, self.pRMax, 2 * self.pDz, self.pSPhi, self.pDPhi, registry=None).pycsgmesh()

    def csgmesh(self):

        pHighNorm = [self.pHighNorm[0].eval(), self.pHighNorm[1].eval(), self.pHighNorm[2].eval()]
        pLowNorm  = [self.pLowNorm[0].eval() , self.pLowNorm[1].eval(),  self.pLowNorm[2].eval()]
                
        zlength = 3 * pDz  # make the dimensions of the semi-infinite plane large enough

        if self.pHighNorm != [0,0,1]:
            pHigh = _Plane("pHigh_temp", pHighNorm, pDz, zlength).pycsgmesh()
            self.mesh = self.mesh.subtract(pHigh)
        if self.pLowNorm != [0,0,-1]:
            pLow  = _Plane("pLow_temp", pLowNorm, -pDz, zlength).pycsgmesh()
            self.mesh = self.mesh.subtract(pLow)
