from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg:
    from ...pycsg.core import CSG as _CSG
    from ...pycsg.geom import Vector as _Vector
    from ...pycsg.geom import Vertex as _Vertex
    from ...pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm:
    from ...pycgal.core import CSG as _CSG
    from ...pycgal.geom import Vector as _Vector
    from ...pycgal.geom import Vertex as _Vertex
    from ...pycgal.geom import Polygon as _Polygon

import numpy as _np

import logging as _log

_log = _log.getLogger(__name__)


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
    :param pDz: full length along z
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

    def __init__(
        self,
        name,
        pRmin1,
        pRmax1,
        pRmin2,
        pRmax2,
        pDz,
        pSPhi,
        pDPhi,
        registry,
        lunit="mm",
        aunit="rad",
        nslice=None,
        addRegistry=True,
    ):
        super().__init__(name, "Cons", registry)

        self.pRmin1 = pRmin1
        self.pRmax1 = pRmax1
        self.pRmin2 = pRmin2
        self.pRmax2 = pRmax2
        self.pDz = pDz
        self.pSPhi = pSPhi
        self.pDPhi = pDPhi
        self.nslice = nslice if nslice else _config.SolidDefaults.Cons.nslice
        self.lunit = lunit
        self.aunit = aunit

        self.dependents = []

        self.varNames = [
            "pRmin1",
            "pRmin2",
            "pRmax1",
            "pRmax2",
            "pDz",
            "pSPhi",
            "pDPhi",
            "nslice",
        ]
        self.varUnits = [
            "lunit",
            "lunit",
            "lunit",
            "lunit",
            "lunit",
            "aunit",
            "aunit",
            None,
        ]

        if addRegistry:
            registry.addSolid(self)

        self.checkParameters()

    def checkParameters(self):
        if self.evaluateParameter(self.pRmin1) > self.evaluateParameter(self.pRmax1):
            msg = "Inner radius must be less than outer radius."
            raise ValueError(msg)
        if self.evaluateParameter(self.pRmin2) > self.evaluateParameter(self.pRmax2):
            msg = "Inner radius must be less than outer radius."
            raise ValueError(msg)
        self._twoPiValueCheck("pDPhi", self.aunit)

    def __repr__(self):
        return f"Cons : {self.name} {self.pRmin1} {self.pRmax1} {self.pRmin2} {self.pRmax2} {self.pDz} {self.pSPhi} {self.pDPhi}"

    def __str__(self):
        return f"Cons : name={self.name} rmin1={float(self.pRmin1)} rmax1={float(self.pRmax1)} rmin2={float(self.pRmin2)} rmax2={float(self.pRmax2)} dz={float(self.pDz)} sphi={float(self.pSPhi)} dphi={float(self.pDPhi)}"

    def mesh(self):
        _log.debug("cons.antlr>")

        from ...gdml import Units as _Units

        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin1 = self.evaluateParameter(self.pRmin1) * luval
        pRmax1 = self.evaluateParameter(self.pRmax1) * luval
        pRmin2 = self.evaluateParameter(self.pRmin2) * luval
        pRmax2 = self.evaluateParameter(self.pRmax2) * luval
        pDz = self.evaluateParameter(self.pDz) * luval / 2.0
        pSPhi = self.evaluateParameter(self.pSPhi) * auval
        pDPhi = self.evaluateParameter(self.pDPhi) * auval

        _log.debug("cons.pycsgmesh>")

        from .GenericPolyhedra import GenericPolyhedra as _GenericPolyhedra

        pZ = [-pDz, -pDz, pDz, pDz]
        pR = [pRmin1, pRmax1, pRmax2, pRmin2]

        ps = _GenericPolyhedra(
            "ps",
            pSPhi,
            pDPhi,
            self.nslice,
            pR,
            pZ,
            self.registry,
            "mm",
            "rad",
            addRegistry=False,
        )
        return ps.mesh()

        return mesh
