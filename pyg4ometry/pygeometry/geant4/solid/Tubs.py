from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
import sys as _sys

import numpy as _np

class Tubs(_SolidBase) :
    """
    Constructs a cylindrical section. 
    
    Inputs:
        name:   string, name of the volume
        pRMin:  float, inner radius
        pRMax:  float, outer radius
        pDz:    float, half-length along z
        pSPhi:  float, starting phi angle
        pDPhi:  float, angle of segment in radians
    """
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi) :
        self.type  = 'Tubs'
        self.name  = name
        self.pRMin = pRMin
        self.pRMax = pRMax
        self.pDz   = pDz
        self.pSPhi = pSPhi
        self.pDPhi = pDPhi
        self.mesh = None
        _registry.addSolid(self)
        
    def __repr__(self) : 
        return 'Tubs : '+self.name+' '+str(self.pRMin)+' '+str(self.pRMax)+' '+str(self.pDz)+' '+str(self.pSPhi)+' '+str(self.pDPhi)
        
    def pycsgmesh(self):
        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self) :
        pDz   = float(self.pDz)
        pRMax = float(self.pRMax)

        self.mesh = _CSG.cylinder(start=[0,0,-pDz], end=[0,0,pDz],radius=pRMax)

    def csgmesh(self) :

        pDz   = float(self.pDz)
        pRMax = float(self.pRMax)
        pRMin = float(self.pRMin)
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)

        wzlength = 3*pDz   # set dimensions of wedge to intersect with that are much larger
                                # than the dimensions of the solid
        wrmax    = 3*pRMax

        if pDPhi == 2*_np.pi :
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi+pDPhi-0.0001, wzlength).pycsgmesh()
        else :
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi+pDPhi, wzlength).pycsgmesh()

        # If a solid cylinder then just return the primitive CSG solid.
        if not pRMin and pSPhi == 0.0 and pDPhi == 2*_np.pi:
            return self.mesh
        if(pRMin):
            sInner = _CSG.cylinder(start=[0,0,-pDz], end=[0,0,pDz],radius=pRMin)
            self.mesh = self.mesh.subtract(sInner).subtract(pWedge.inverse())
        else:
            self.mesh = self.mesh.subtract(pWedge.inverse())

        return self.mesh


