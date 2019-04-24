from SolidBase import SolidBase as _SolidBase

from Tubs import Tubs as _Tubs
from Plane import Plane as _Plane

import numpy as _np
import logging as _log

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
        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        # Low norm and high norm exlcluded as they are lists
        return "Cut tubs : {} {} {} {} {} {}".format(self.name, self.pRMin, self.pRMax,
                                                        self.pDz, self.pSPhi, self.pDPhi)
    def pycsgmesh(self):

        _log.info('cuttubs.pycsgmesh> antlr')
        pRMin     = float(self.pRMin)
        pRMax     = float(self.pRMax)
        pDz       = float(self.pDz)
        pSPhi     = float(self.pSPhi)
        pDPhi     = float(self.pDPhi)
        pHighNorm = [self.pHighNorm[0].eval(), self.pHighNorm[1].eval(), self.pHighNorm[2].eval()]
        pLowNorm  = [self.pLowNorm[0].eval() , self.pLowNorm[1].eval(),  self.pLowNorm[2].eval()]

        _log.info('cuttubs.pycsgmesh> mesh')
        mesh = _Tubs("tubs_temp", self.pRMin, self.pRMax, 2 * self.pDz, self.pSPhi, self.pDPhi, registry=None).pycsgmesh()

        if pLowNorm != [0,0,-1] or pHighNorm != [0,0,1]:
                
            zlength = 3 * pDz  # make the dimensions of the semi-infinite plane large enough
            
            if pHighNorm != [0,0,1]:
                pHigh = _Plane("pHigh_temp", pHighNorm, pDz, zlength).pycsgmesh()
                mesh = mesh.subtract(pHigh)
            if pLowNorm != [0,0,-1]:
                pLow  = _Plane("pLow_temp", pLowNorm, -pDz, zlength).pycsgmesh()
                mesh = mesh.subtract(pLow)
                
            return mesh
        else : 
            return mesh
