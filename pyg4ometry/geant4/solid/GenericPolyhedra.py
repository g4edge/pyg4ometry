from SolidBase import SolidBase as _SolidBase
from Polyhedra import Polyhedra

import logging as _log
import numpy as _np

class GenericPolyhedra(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, numSide, pZ, pR,
                 registry, lunit="mm", aunit="rad", addRegistry=True):
        """
        Constructs a solid of rotation using an arbitrary 2D surface defined by a series of (r,z) coordinates.

        Inputs:
        name = name
        pSPhi = Angle Phi at start of rotation
        pDPhi = Angle Phi at end of rotation
        numSide = number of polygon sides
        pR = r coordinate list
		pZ = z coordinate list
        """
        self.type    = 'GenericPolyhedra'
        self.name    = name
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.numSide = numSide
        self.pR      = pR
        self.pZ      = pZ

        self.lunit   = lunit
        self.aunit   = aunit

        self.varNames = ["pSPhi", "pDPhi", "numSide", "pR","pZ","lunit","aunit"]

        self.dependents = []

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Generic Polyhedra : {} {} {} {}".format(self.name, self.pSPhi,
                                                        self.pDPhi, self.numSide)

    def checkParameters(self):
        if len(self.pR) < 3:
            raise ValueError("Generic Polyhedra must have at least 3 R-Z points defined")

    def pycsgmesh(self):
        _log.info("genericpolyhedra.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval
        numSide = self.evaluateParameter(self.numSide)
        pR = [val*luval for val in self.evaluateParameter(self.pR)]
        pZ = [val*luval for val in self.evaluateParameter(self.pZ)]

        _log.info("genericpolyhedra.pycsgmesh>")
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
        _poly = Polyhedra("temp", pSPhi, pDPhi, numSide, len(pZ), pZ, pRMin, pR,
                          registry=self.registry, lunit="mm", aunit="rad", addRegistry=False)

        return _poly.pycsgmesh()
