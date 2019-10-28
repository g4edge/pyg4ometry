from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG

import logging as _log

class Scaled(_SolidBase):
    """
    Constructs a scaled sold. 

    :param name: of solid for registry
    :type name: str
    :poram solid: reference for scaling
    :type solid: SolidBase
    :param pX: scale in x
    :type pX: float, Constant, Quantity, Variable, Expression
    :param pY: scale in y
    :type pY: float, Constant, Quantity, Variable, Expression
    :param pZ: scale in z
    :type pZ: float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    """

    def __init__(self, name, solid, pX, pY, pZ, registry, addRegistry=True):
        self.name = name
        self.solid = solid
        self.pX   = pX
        self.pY   = pY
        self.pZ   = pZ
        self.type = 'Scaled'

        self.varNames = ["pX", "pY", "pZ"]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Scaled : {} {} {} {} {}".format(self.name, self.solid, self.pX, self.pY, self.pZ)

    def pycsgmesh(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        _log.info('scaled.pycsgmesh> antlr')

        pX = self.evaluateParameter(self.pX)
        pY = self.evaluateParameter(self.pY)
        pZ = self.evaluateParameter(self.pZ)

        mesh = self.solid.pycsgmesh()
        mesh.scale([pX,pY,pZ])

        _log.info('scaled.pycsgmesh> mesh')
        return mesh

