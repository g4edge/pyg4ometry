from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from Polycone import Polycone as _Polycone
import numpy as _np
import logging as _log

class Polyhedra(_SolidBase):
    def __init__(self, name, phiStart, phiTotal, numSide, numZPlanes,
                 zPlane, rInner, rOuter, registry=True, lunit = "mm", aunit ="rad"):
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
        self.lunit      = lunit
        self.aunit      = aunit
        
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

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        phiStart = float(self.phiStart)*auval
        phiTotal = float(self.phiTotal)*auval
        numSide = int(float(self.numSide))
        numZPlanes = int(self.numZPlanes)
        zPlane = [float(val)*luval for val in self.zPlane]
        rInner = [float(val)*luval for val in self.rInner]
        rOuter = [float(val)*luval for val in self.rOuter]

        _log.info("polyhedra.pycsgmesh>")
        fillfrac  = phiTotal/(2*_np.pi)
        slices    = (numSide)/fillfrac

        ph        = _Polycone(self.name, phiStart, phiTotal,
                              zPlane, rInner, rOuter,
                              registry=None,
                              lunit="mm",
                              aunit="rad",
                              nslice=int(_np.ceil(slices)))
        mesh = ph.pycsgmesh()

        return mesh
