from SolidBase import SolidBase as _SolidBase
from Polyhedra import Polyhedra

import logging as _log
import numpy as _np

class GenericPolyhedra(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, numSide, pR, pZ,
                 registry=None,
                 lunit="mm",
                 aunit="rad"):
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

        self.dependents = []

        self.checkParameters()
        if registry:
            registry.addSolid(self)

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

        pSPhi = float(self.pSPhi)*auval
        pDPhi = float(self.pDPhi)*auval
        numSide = float(self.numSide)
        pR = [float(val)*luval for val in self.pR]
        pZ = [float(val)*luval for val in self.pZ]

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
