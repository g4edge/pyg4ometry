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

    :param name: of the solid
    :type name: str
    :param pRMin1: inner radius at -pDz/2
    :type pRMin1: float, Constant, Quantity, Variable
    :param pRMax1: outer radius at -pDz/2
    :type pRMax1: float, Constant, Quantity, Variable
    :param pRMin2: inner radius at +pDZ/2
    :type pRMin2: float, Constant, Quantity, Variable
    :param pRMax2: outer radius at +pDz/2
    :type pRMax2: float, Constant, Quantity, Variable
    :param pDz: length along z
    :type pDz: float, Constant, Quantity, Variable
    :param pSPhi: starting phi angle
    :type pSPhi: float, Constant, Quantity, Variable
    :param pDPhi: angle of segment in radians
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

    def __init__(self, name, pRmin1, pRmax1, pRmin2, pRmax2, pDz,
                 pSPhi, pDPhi, registry, lunit="mm", aunit="rad",
                 nslice=16, addRegistry=True):

        self.name   = name
        self.type   = 'Cons'
        self.pRmin1 = pRmin1
        self.pRmax1 = pRmax1
        self.pRmin2 = pRmin2
        self.pRmax2 = pRmax2
        self.pDz    = pDz
        self.pSPhi  = pSPhi
        self.pDPhi  = pDPhi
        self.nslice = nslice
        self.lunit  = lunit
        self.aunit  = aunit

        self.dependents = []

        self.varNames = ["pRMin", "pRmin1", "pRmax1","pRmin2","pRmax2","pDz","pSPhi","pDPhi"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

        self.checkParameters()

    def checkParameters(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        auval = _Units.unit(self.aunit)

        if self.evaluateParameter(self.pRmin1) > self.evaluateParameter(self.pRmax1) :
            raise ValueError("Inner radius must be less than outer radius.")
        if self.evaluateParameter(self.pRmin2) > self.evaluateParameter(self.pRmax2) :
            raise ValueError("Inner radius must be less than outer radius.")
        if self.evaluateParameter(self.pDPhi)*auval > _np.pi*2:
            raise ValueError("pDPhi must be less than 2 pi")

    def __repr__(self):
        return "Cons : {} {} {} {} {} {} {} {}".format(self.name, self.pRmin1, self.pRmax1,
                                                       self.pRmin2, self.pRmax2, self.pDz,
                                                       self.pSPhi, self.pDPhi)
    def pycsgmesh(self):

        _log.info('cons.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin1 = self.evaluateParameter(self.pRmin1)*luval
        pRmax1 = self.evaluateParameter(self.pRmax1)*luval
        pRmin2 = self.evaluateParameter(self.pRmin2)*luval
        pRmax2 = self.evaluateParameter(self.pRmax2)*luval
        pDz    = self.evaluateParameter(self.pDz)*luval/2.0
        pSPhi  = self.evaluateParameter(self.pSPhi)*auval
        pDPhi  = self.evaluateParameter(self.pDPhi)*auval

        _log.info('cons.pycsgmesh>')

        if pRmax1 < pRmax2:
            R1 = pRmax2  # Cone with tip pointing towards -z
            r1 = pRmin2
            R2 = pRmax1
            r2 = pRmin1
            sign = -1
        else:
            R1 = pRmax1  # Cone with tip pointing towards +z
            r1 = pRmin1
            R2 = pRmax2
            r2 = pRmin2
            sign = 1

        h = 2 * pDz

        H1 = float(R2 * h) / float(R1 - R2) if R1 != R2 else 0
        H2 = float(r2 * h) / float(r1 - r2) if r1 != r2 else 0

        h1 = sign * (h + H1)
        h2 = sign * (h + H2)

        # basic cone mesh
        outer_solid = _CSG.cylinder if R1 == R2 else _CSG.cone
        mesh = outer_solid(start=[0, 0, -sign * pDz], end=[0, 0, h1 - sign * pDz],
                           radius=R1, slices=self.nslice)

        # ensure radius for intersection wedge is much bigger than solid
        wrmax = 3 * (pRmax1 + pRmax2)
        wzlength = h*5

        if pDPhi != 2 * _np.pi:
            pWedge = _Wedge("wedge_temp", wrmax, pSPhi, pSPhi + pDPhi, wzlength).pycsgmesh()
        else:
            pWedge = _CSG.cylinder(start=[0, 0, -wzlength/2.], end=[0, 0, wzlength/2.],
                                   radius=wrmax)

        pTopCut = _Plane("pTopCut_temp", _Vector(0, 0, 1), pDz, wzlength).pycsgmesh()
        pBotCut = _Plane("pBotCut_temp", _Vector(0, 0, -1), -pDz, wzlength).pycsgmesh()

        if r1 or r2:
            inner_solid = _CSG.cylinder if r1 == r2 else _CSG.cone
            sInner = inner_solid(start=[0, 0, -sign * pDz], end=[0, 0, h2 - sign * pDz], radius=r1)
            mesh = mesh.subtract(sInner).intersect(pWedge).subtract(pBotCut).subtract(pTopCut)
        else:
            mesh = mesh.intersect(pWedge).subtract(pBotCut).subtract(pTopCut)

        return mesh
