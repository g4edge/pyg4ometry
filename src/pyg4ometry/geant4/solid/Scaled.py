import logging as _log

from .SolidBase import SolidBase as _SolidBase


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
        super().__init__(name, "Scaled", registry)

        self.solid = solid
        self.pX = pX
        self.pY = pY
        self.pZ = pZ

        self.varNames = ["pX", "pY", "pZ"]
        self.varUnits = [None, None, None]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return f"Scaled : {self.name} {self.solid} {self.pX} {self.pY} {self.pZ}"

    def mesh(self):

        _log.info("scaled.pycsgmesh> antlr")

        pX = self.evaluateParameter(self.pX)
        pY = self.evaluateParameter(self.pY)
        pZ = self.evaluateParameter(self.pZ)

        mesh = self.solid.mesh()
        mesh.scale([pX, pY, pZ])

        _log.info("scaled.pycsgmesh> mesh")
        return mesh
