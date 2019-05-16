from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Polygon as _Polygon
from Wedge import Wedge as _Wedge
import sys as _sys

import numpy as _np
import logging as _log

class Tubs(_SolidBase):
    """
    Constructs a cylindrical section.

    :param name: of object in registry
    :type name: str
    :param pRMin: inner radius
    :type pRMin: float
    :param pRMax: outer radius
    :type pRMax: float
    :param pDz: half-length along z
    :type pDz: float
    :param pSPhi: starting phi angle
    :type pSPhi: float
    :param pDPhi: angle of segment in phi
    :type pDPhi: float
    """
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi, registry=None,
                 lunit="mm", aunit="rad", nslice=16):
        self.type   = 'Tubs'
        self.name   = name
        self.pRMin  = pRMin
        self.pRMax  = pRMax
        self.pDz    = pDz
        self.pSPhi  = pSPhi
        self.pDPhi  = pDPhi
        self.lunit   = lunit
        self.aunit  = aunit
        self.nslice = nslice
        self.mesh   = None
        self.dependents = []
        if registry :
            registry.addSolid(self)

    def __repr__(self):
        return "Tubs : {} {} {} {} {} {}".format(self.name, self.pRMin, self.pRMax,
                                                 self.pDz, self.pSPhi, self.pDPhi)

    def pycsgmesh(self):
        _log.info('tubs.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pDz   = float(self.pDz)*luval
        pRMax = float(self.pRMax)*luval
        pRMin = float(self.pRMin)*luval
        pSPhi = float(self.pSPhi)*auval
        pDPhi = float(self.pDPhi)*auval-0.001 # issue with 2*pi
        pDz   = float(self.pDz)*luval/2
        pRMax = float(self.pRMax)*luval

        _log.info('tubs.pycsgmesh> mesh')
        mesh = _CSG.cylinder(start=[0,0,-pDz], end=[0,0,pDz],radius=pRMax, slices=self.nslice)

        wzlength = 3*pDz    # set dimensions of wedge to intersect with that are much larger
                            # than the dimensions of the solid
        wrmax    = 3*pRMax

        if pDPhi == 2*_np.pi:
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi+pDPhi-0.0001, wzlength).pycsgmesh()
        else:
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi+pDPhi, wzlength).pycsgmesh()

        # If a solid cylinder then just return the primitive CSG solid.
        if not pRMin and pSPhi == 0.0 and pDPhi == 2*_np.pi:
            return mesh
        if(pRMin):
            sInner = _CSG.cylinder(start=[0,0,-pDz], end=[0,0,pDz],radius=pRMin, slices=self.nslice)
            mesh = mesh.subtract(sInner).subtract(pWedge.inverse())
        else:
            mesh = mesh.subtract(pWedge.inverse())

        return mesh
