from SolidBase import SolidBase as _SolidBase
from Polycone import Polycone

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

    def __init__(self, name, pSPhi, pDPhi, pR, pZ,
                 registry, lunit="mm", aunit="rad", nslice=16,
                 addRegistry=True):

        self.type    = 'GenericPolycone'
        self.name    = name
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pR      = pR
        self.pZ      = pZ
        self.lunit   = lunit
        self.aunit   = aunit
        self.nslice  = nslice

        self.varNames = ["pSPhi", "pDPhi", "pR", "pZ"]

        self.dependents = []

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def checkParameters(self):
        if len(self.pR) < 3:
            raise ValueError("Generic Polycone must have at least 3 R-Z points defined")

    def pycsgmesh(self):
        _log.info("genericpolycone.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 
        
        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval
        pR = [val*luval for val in self.evaluateParameter(self.pR)]
        pZ = [val*luval for val in self.evaluateParameter(self.pZ)]

        _log.info("genericpolycone.pycsgmesh>")
        r_first = pR[0]
        r_last = pR[-1]
        z_first = pZ[0]
        z_last = pZ[-1]
        pRMin = []
        for i, r in enumerate(pR):
            #linear interpolation
            r = (r_first*(z_last-pZ[i]) + r_last*(pZ[i]-z_first))/(z_last - z_first)
            pRMin.append(r)

        # Use a proxy polycone to get the mesh
        _poly = Polycone("temp", pSPhi, pDPhi, pZ, pRMin, pR,
                         registry=self.registry,
                         lunit="mm", aunit="rad",
                         nslice=self.nslice, addRegistry=False)

        return _poly.pycsgmesh()
