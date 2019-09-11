from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG

import logging as _log

class Box(_SolidBase):
    """
    Constructs a box. Note the lengths are full lengths and not half lengths as in Geant4

    :param name: of solid for registry
    :type name: str
    :param pX: length along x
    :type pX: float, Constant, Quantity, Variable, Expression
    :param pY: length along y
    :type pY: float, Constant, Quantity, Variable, Expression
    :param pZ: length along z
    :type pZ: float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    """

    def __init__(self, name, pX, pY, pZ, registry, lunit="mm", addRegistry=True):
        self.type = 'Box'
        self.name = name

        if addRegistry:
            registry.addSolid(self)
        self.registry = registry

        self.dependents = []
        self.varNames = ["pX", "pY", "pZ", "lunit"]

        for name in self.varNames:
            self._addProperty(name)
            setattr(self, name, locals()[name])

    def __repr__(self):
        return "Box : {} {} {} {}".format(self.name, self.pX, self.pY, self.pZ)

    def pycsgmesh(self):
        _log.info('box.pycsgmesh> antlr')
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        uval = _Units.unit(self.lunit)

        pX = self.evaluateParameter(self.pX)*uval/2.0
        pY = self.evaluateParameter(self.pY)*uval/2.0
        pZ = self.evaluateParameter(self.pZ)*uval/2.0

        _log.info('box.pycsgmesh> mesh')
        mesh = _CSG.cube(center=[0,0,0], radius=[pX,pY,pZ])
        return mesh

