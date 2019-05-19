from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import logging as _log
import numpy as _np

class Orb(_SolidBase):
    """
    Constructs a solid sphere.
    
    :param name: of the sold
    :type name: str
    :param pRMax: outer radius
    :type pRMax: float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int     
    """

    def __init__(self, name, pRMax, registry=None, lunit = "mm", nslice=16, nstack=16):
        self.type = 'Orb'
        self.name = name
        self.pRMax = pRMax
        self.lunit = lunit
        self.nslice = nslice
        self.nstack = nstack

        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Orb : {} {}".format(self.name, self.pRMax)

    def pycsgmesh(self):
        _log.info("orb.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pRMax = float(self.pRMax)*luval

        _log.info("orb.pycsgmesh>")
        mesh = _CSG.sphere(center=[0,0,0], radius=pRMax,
                           slices=self.nslice, stacks=self.nstack)
        return mesh
