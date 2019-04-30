from SolidBase import SolidBase as _SolidBase
from Polycone import Polycone

import logging as _log
import numpy as _np

class GenericPolycone(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, pR, pZ,
                 registry=None, nslice=16):
        """
        Constructs a solid of rotation using an arbitrary 2D surface defined by a series of (r,z) coordinates.

        Inputs:
        name = name
        pSPhi = Angle Phi at start of rotation
        pDPhi = Angle Phi at end of rotation
        pR = r coordinate list
		pZ = z coordinate list
        """
        self.type    = 'GenericPolycone'
        self.name    = name
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pR   = pR
        self.pZ   = pZ
        self.nslice  = nslice

        self.dependents = []

        self.checkParameters()
        if registry:
            registry.addSolid(self)

    def checkParameters(self):
        if len(self.pR) < 3:
            raise ValueError("Generic Polycone must have at least 3 R-Z points defined")

    def pycsgmesh(self):
        _log.info("genericpolycone.antlr>")
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)
        pR = [float(val) for val in self.pR]
        pZ = [float(val) for val in self.pZ]

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
                         registry=None, nslice=self.nslice)

        return _poly.pycsgmesh()
