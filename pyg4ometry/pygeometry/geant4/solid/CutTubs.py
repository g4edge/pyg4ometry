from SolidBase import SolidBase as _SolidBase
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Tubs import Tubs as _Tubs
from pygeometry.geant4.solid.Plane import Plane as _Plane

import numpy as _np

class CutTubs(_SolidBase) :
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
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi, pLowNorm, pHighNorm) :
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
        _registry.addSolid(self)

    def __repr__(selfs):
        pass

    def pycsgmesh(self):
#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        if self.pLowNorm != [0,0,-1] or self.pHighNorm != [0,0,1] :
            self.csgmesh()

        return self.mesh

    def basicmesh(self):
        self.mesh = _Tubs("tubs_temp", self.pRMin, self.pRMax, 2 * self.pDz, self.pSPhi, self.pDPhi).pycsgmesh()

    def csgmesh(self):
        zlength = 3 * self.pDz  # make the dimensions of the semi-infinite plane large enough
        if self.pHighNorm != [0,0,1] :
            pHigh = _Plane("pHigh_temp", self.pHighNorm, self.pDz, zlength).pycsgmesh()
            self.mesh = self.mesh.subtract(pHigh)
        if self.pLowNorm != [0,0,-1] :
            pLow  = _Plane("pLow_temp", self.pLowNorm, -self.pDz, zlength).pycsgmesh()
            self.mesh = self.mesh.subtract(pLow)
