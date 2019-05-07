from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG
from Plane import Plane as _Plane
from Wedge import Wedge as _Wedge
from pyg4ometry.pycsg.geom import Vector as _Vector
import numpy as _np

import logging as _log

class Cons(_SolidBase):
    """
    Constructs a conical section.

    Inputs:
        name:      string, name of the volume
        pRMin1:    float, inner radius at -pDz
        pRMax1:    float, outer radius at -pDz
        pRMin2:    float, inner radius at +pDZ
        pRMax2:    float, outer radius at +pDz
        pDz:       float, half-length along z
        pSPhi:     float, starting phi angle
        pDPhi:     float, angle of segment in radians
    """

    def __init__(self, name, pRmin1, pRmax1, pRmin2, pRmax2, pDz,
                 pSPhi, pDPhi, registry=None, nslice=16):

        self.name = name
        self.type = 'Cons'
        self.pRmin1 = pRmin1
        self.pRmax1 = pRmax1
        self.pRmin2 = pRmin2
        self.pRmax2 = pRmax2
        self.pDz = pDz
        self.pSPhi = pSPhi
        self.pDPhi = pDPhi
        self.nslice = nslice

        self.dependents = []

        if registry:
            registry.addSolid(self)
        # self.checkParameters()

    def checkParameters(self):
        if self.pRmin1 > self.pRmax1:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pRmin2 > self.pRmax2:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pDPhi > _np.pi*2:
            raise ValueError("pDTheta must be less than 2 pi")

    def __repr__(self):
        return "Cons : {} {} {} {} {} {} {} {}".format(self.name, self.pRmin1, self.pRmax1,
                                                       self.pRmin2, self.pRmax2, self.pDz,
                                                       self.pSPhi, self.pDPhi)
    def pycsgmesh(self):

        _log.info('cons.antlr>')
        pRmin1 = float(self.pRmin1)
        pRmax1 = float(self.pRmax1)
        pRmin2 = float(self.pRmin2)
        pRmax2 = float(self.pRmax2)
        pDz    = float(self.pDz)
        pSPhi  = float(self.pSPhi)
        pDPhi  = float(self.pDPhi)

        _log.info('cons.pycsgmesh>')
        if pRmax1 < pRmax2:
            R1 = pRmax2  # Cone with tip pointing towards -z
            r1 = pRmin2
            R2 = pRmax1
            r2 = pRmin1
            factor = -1

        else:
            R1 = pRmax1  # Cone with tip pointing towards +z
            r1 = pRmin1
            R2 = pRmax2
            r2 = pRmin2
            factor = 1

        h = 2 * pDz
        H1 = float(R2 * h) / float(R1 - R2)

        try:  # Avoid crash when both inner radii are 0
            H2 = float(r2 * h) / float(r1 - r2)
        except ZeroDivisionError:
            H2 = 0
        
        h1 = factor * (h + H1)
        h2 = factor * (h + H2)

        # basic cone mesh
        mesh = _CSG.cone(start=[0, 0, -factor * pDz], end=[0, 0, h1 - factor * pDz],
                         radius=R1, slices=self.nslice)

        # ensure radius for intersection wedge is much bigger than solid
        wrmax = 3 * (pRmax1 + pRmax2)

        # ensure the plane is large enough to cut cone correctly. Extroplates the z intersect using two points.
        wzlength = abs((pRmax2*((2*pDz)/(pRmax2 - pRmax1))) + pDz)

        if pDPhi != 2 * _np.pi:
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi + pDPhi, wzlength).pycsgmesh()
        else:
            pWedge = _CSG.cylinder(start=[0, 0, -pDz * 5], end=[0, 0, pDz * 5],
                                   radius=R1 * 5)  # factor 5 is just to ensure wedge mesh is much bigger than cone solid

        pTopCut = _Plane("pTopCut_temp", _Vector(0, 0, 1), pDz, wzlength).pycsgmesh()
        pBotCut = _Plane("pBotCut_temp", _Vector(0, 0, -1), -pDz, wzlength).pycsgmesh()

        if H2:
            sInner = _CSG.cone(start=[0, 0, -factor * pDz], end=[0, 0, h2 - factor * pDz], radius=r1)
            mesh = mesh.subtract(sInner).intersect(pWedge).subtract(pBotCut).subtract(pTopCut)
        else:
            mesh = mesh.intersect(pWedge).subtract(pBotCut).subtract(pTopCut)

        return mesh
