from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Plane import Plane as _Plane
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
from pygeometry.pycsg.geom import Vector as _Vector
import numpy as _np

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

    def __init__(self, name, pRmin1, pRmax1, pRmin2, pRmax2, pDz, pSPhi, pDPhi):
        self.name = name
        self.type = 'Cons'
        self.pRmin1 = pRmin1
        self.pRmax1 = pRmax1
        self.pRmin2 = pRmin2
        self.pRmax2 = pRmax2
        self.pDz = pDz
        self.pSPhi = pSPhi
        self.pDPhi = pDPhi
        self.mesh = None
        _registry.addSolid(self)
        self.checkParameters()

    def checkParameters(self):
        if self.pRmin1 > self.pRmax1:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pRmin2 > self.pRmax2:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pDPhi > _np.pi*2:
            raise ValueError("pDTheta must be less than 2 pi")

    def pycsgmesh(self):
        self.basicmesh()
        self.csgmesh()

        return self.mesh


    def basicmesh(self):
        if self.pRmax1 < self.pRmax2:
            self.R1 = self.pRmax2  # Cone with tip pointing towards -z
            self.r1 = self.pRmin2
            self.R2 = self.pRmax1
            self.r2 = self.pRmin1
            self.factor = -1

        else:
            self.R1 = self.pRmax1  # Cone with tip pointing towards +z
            self.r1 = self.pRmin1
            self.R2 = self.pRmax2
            self.r2 = self.pRmin2
            self.factor = 1

        h = 2 * self.pDz
        self.H1 = float(self.R2 * h) / float(self.R1 - self.R2)

        try:  # Avoid crash when both inner radii are 0
            self.H2 = float(self.r2 * h) / float(self.r1 - self.r2)
        except ZeroDivisionError:
            self.H2 = 0

        self.h1 = self.factor * (h + self.H1)
        self.h2 = self.factor * (h + self.H2)

        self.mesh = _CSG.cone(start=[0, 0, -self.factor * self.pDz], end=[0, 0, self.h1 - self.factor * self.pDz], radius=self.R1)

        return self.mesh

    def csgmesh(self):

        
        # ensure radius for intersection wedge is much bigger than solid
        wrmax = 3 * (self.pRmax1 + self.pRmax2)
        # ensure the plane is large enough to cut cone correctly. Extroplates the z intersect using two points.
        wzlength = abs((self.pRmax2*((2*self.pDz)/(self.pRmax2 - self.pRmax1))) + self.pDz)   

        if self.pDPhi != 2 * _np.pi:
            pWedge = _Wedge("wedge_temp", wrmax, self.pSPhi, self.pSPhi + self.pDPhi, wzlength).pycsgmesh()
        else:
            pWedge = _CSG.cylinder(start=[0, 0, -self.pDz * 5], end=[0, 0, self.pDz * 5],
                                   radius=self.R1 * 5)  # factor 5 is just to ensure wedge mesh is much bigger than cone solid

        pTopCut = _Plane("pTopCut_temp", _Vector(0, 0, 1), self.pDz, wzlength).pycsgmesh()
        pBotCut = _Plane("pBotCut_temp", _Vector(0, 0, -1), -self.pDz, wzlength).pycsgmesh()

        if self.H2:
            sInner = _CSG.cone(start=[0, 0, -self.factor * self.pDz], end=[0, 0, self.h2 - self.factor * self.pDz], radius=self.r1)
            self.mesh = self.mesh.subtract(sInner).intersect(pWedge).subtract(pBotCut).subtract(pTopCut)
        else:
            self.mesh = self.mesh.intersect(pWedge).subtract(pBotCut).subtract(pTopCut)

        return self.mesh
