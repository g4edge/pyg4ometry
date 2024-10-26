from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from .GenericPolyhedra import GenericPolyhedra as _GenericPolyhedra

import logging as _log
import numpy as _np


class GenericPolycone(_SolidBase):
    """
    Constructs a solid of rotation using an arbitrary 2D surface defined by a series of (r,z) coordinates.

    :param name: of solid
    :type name: str
    :param pSPhi: angle phi at start of rotation
    :type pSPhi: float, Constant, Quantity, Variable, Expression
    :param pDPhi: angle Phi at end of rotation
    :type pDPhi: float, Constant, Quantity, Variable, Expression
    :param pR: r coordinate
    :type pR: list of float, Constant, Quantity, Variable, Expression
    :param pZ: z coordinate
    :type pZ: list of float, Constant, Quantity, Variable, Expression
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
        pSPhi,
        pDPhi,
        pR,
        pZ,
        registry,
        lunit="mm",
        aunit="rad",
        nslice=None,
        addRegistry=True,
    ):
        super().__init__(name, "GenericPolycone", registry)

        self.pSPhi = pSPhi
        self.pDPhi = pDPhi
        self.pR = pR
        self.pZ = pZ
        self.lunit = lunit
        self.aunit = aunit
        self.nslice = nslice if nslice else _config.SolidDefaults.GenericPolycone.nslice

        self.varNames = ["pSPhi", "pDPhi", "pR", "pZ"]
        self.varUnits = ["aunit", "aunit", "lunit", "lunit"]

        self.dependents = []

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        # TODO put a proper string in here
        return f"GenericPolycone solid: {self.name}"

    def __str__(self):
        # TODO put a proper string in here
        return f"GenericPolycone solid: name={self.name}"

    def checkParameters(self):
        if len(self.pR) < 3:
            msg = "Generic Polycone must have at least 3 R-Z points defined"
            raise ValueError(msg)

    def mesh(self):
        _log.info("genericpolycone.antlr>")

        from ...gdml import Units as _Units

        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pSPhi = self.evaluateParameter(self.pSPhi) * auval
        pDPhi = self.evaluateParameter(self.pDPhi) * auval
        pR = [val * luval for val in self.evaluateParameter(self.pR)]
        pZ = [val * luval for val in self.evaluateParameter(self.pZ)]

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
