from .GenericPolyhedra import GenericPolyhedra as  _GenericPolyhedra
from .SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from .Polycone import Polycone as _Polycone
import numpy as _np
import logging as _log

class Polyhedra(_SolidBase):
    """
    Constructs a polyhedra.
    
    :param name:       of solid
    :type name:        str
    :param phiStart:   start phi angle
    :type phiStart:    float, Constant, Quantity, Variable, Expression
    :param phiTotal:   delta phi angle
    :type phiTotal:    float, Constant, Quantity, Variable, Expression
    :param numSide:    number of sides
    :type numSide:     int
    :param numZPlanes: number of planes along z
    :type numZPlanes:  int 
    :param zPlane:     position of z planes
    :type zPlane:      list of float, Constant, Quantity, Variable, Expression
    :param rInner:     tangent distance to inner surface per z plane
    :type rInner:      list of float, Constant, Quantity, Variable, Expression
    :param rOuter:     tangent distance to outer surface per z plane
    :type rOuter:      list of float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str 
    
    """

    def __init__(self, name, phiStart, phiTotal, numSide, numZPlanes,
                 zPlane, rInner, rOuter, registry, lunit="mm", aunit="rad",
                 addRegistry=True):

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

        self.varNames = ["phiStart", "phiTotal", "numSide", "numZPlanes","zPlane","rInner","rOuter"]

        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

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

        phiStart = self.evaluateParameter(self.phiStart)*auval
        phiTotal = self.evaluateParameter(self.phiTotal)*auval

        numSide = int(self.evaluateParameter(self.numSide))
        numZPlanes = int(self.numZPlanes)
        zPlane = [val*luval for val in self.evaluateParameter(self.zPlane)]
        rInner = [val*luval for val in self.evaluateParameter(self.rInner)]
        rOuter = [val*luval for val in self.evaluateParameter(self.rOuter)]

        pZ = []
        pR = []

        # first point or rInner
        pZ.append(zPlane[0])
        pR.append(rInner[0])

        # rest of outer
        pZ.extend(zPlane)
        pR.extend(rOuter)

        # reversed inner
        pZ.extend(zPlane[-1:0:-1])
        pR.extend(rInner[-1:0:-1])

        ps = _GenericPolyhedra("ps", phiStart, phiTotal, numSide, pR, pZ, self.registry, "mm", "rad", addRegistry=False)

        return ps.pycsgmesh()

