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

    :param name: of solid for registry
    :type name: str
    :param pRMin: inner radius
    :type pRMin: float, Constant, Quantity, Variable
    :param pRMax: outer radius
    :type pRMax: float, Constant, Quantity, Variable
    :param pDz: length along z
    :type pDz: float, Constant, Quantity, Variable
    :param pSPhi: starting phi angle
    :type pSPhi: float, Constant, Quantity, Variable
    :param pDPhi: angle of segment in phi
    :type pDPhi: float, Constant, Quantity, Variable
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int 
    """
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi, registry=None,
                 lunit="mm", aunit="rad", nslice=16, addRegistry=True):
        self.name   = name
        self.type   = 'Tubs'

        if addRegistry :
            registry.addSolid(self)
        self.registry = registry

        self.dependents = []
        self.varNames = ["pRMin", "pRMax", "pDz", "pSPhi",
                         "pDPhi", "aunit", "lunit", "nslice"]

        for name in self.varNames:
            self._addProperty(name)
            setattr(self, name, locals()[name])


    def __repr__(self):
        return "Tubs : {} {} {} {} {} {}".format(self.name, self.pRMin, self.pRMax,
                                                 self.pDz, self.pSPhi, self.pDPhi)

    def pycsgmesh(self):
        _log.info('tubs.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pDz   = self.evaluateParameter(self.pDz)*luval
        pRMax = self.evaluateParameter(self.pRMax)*luval
        pRMin = self.evaluateParameter(self.pRMin)*luval
        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval-0.001 # issue with 2*pi
        pDz   = self.evaluateParameter(self.pDz)*luval/2
        pRMax = self.evaluateParameter(self.pRMax)*luval

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
