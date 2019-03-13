from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from Polycone import Polycone as _Polycone
import numpy as _np
import logging as _log

class Polyhedra(_SolidBase):
    def __init__(self, name, phiStart, phiTotal, numSide, numZPlanes,
                 zPlane, rInner, rOuter, registry=True):
        """
        Constructs a polyhedra.

        Inputs:
          name:       string, name of the volume
          phiStart:   float, start phi angle
          phiTotal:   float, delta phi angle
          numSide:    int, number of sides
          numZPlanes: int, number of planes along z
          zPlane:     list, position of z planes
          rInner:     list, tangent distance to inner surface per z plane
          rOuter:     list, tangent distance to outer surface per z plane

        """
        self.type       = 'Polyhedra'
        self.name       = name
        self.phiStart   = phiStart
        self.phiTotal   = phiTotal
        self.numSide    = numSide
        self.numZPlanes = numZPlanes
        self.zPlane     = zPlane
        self.rInner     = rInner
        self.rOuter     = rOuter

        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Polyhedra : {} {} {} {} {}".format(self.name, self.phiStart,
                                                  self.phiTotal, self.numSide,
                                                  self.numZPlanes)

    def pycsgmesh(self):
        mesh = self.basicmesh()
        return mesh

    def basicmesh(self):
        _log.info("polyhedra.antlr>")

        phiStart = float(self.phiStart)
        phiTotal = float(self.phiTotal)
        numSide = int(self.numSide)
        numZPlanes = int(self.numZPlanes)
        zPlane = [float(val) for val in self.zPlane]
        rInner = [float(val) for val in self.rInner]
        rOuter = [float(val) for val in self.rOuter]

        _log.info("polyhedra.pycsgmesh>")
        fillfrac  = phiTotal/(2*_np.pi)
        slices    = (numSide)/fillfrac

        ph        = _Polycone(self.name, phiStart, phiTotal,
                              zPlane, rInner, rOuter,
                              nslice=int(_np.ceil(slices)), registry=None)
        mesh = ph.pycsgmesh()

        return mesh
