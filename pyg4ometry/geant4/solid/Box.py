from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG

import logging as _log

class Box(_SolidBase):
    """
    Constructs a box.

    :param name: of object in registry
    :type name: str
    :param pX: Length along x
    :type name: float
    :param pY: Length along y
    :type name: float
    :param pZ: Length along z
    :type name: float
    """

    def __init__(self, name, pX, pY, pZ, registry=None, lunit="mm",):
        self.name = name
        self.pX   = pX
        self.pY   = pY
        self.pZ   = pZ
        self.lunit = lunit
        self.type = 'Box'
        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Box : {} {} {} {}".format(self.name, self.pX, self.pY, self.pZ)

    def pycsgmesh(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        _log.info('box.pycsgmesh> antlr')

        uval = _Units.unit(self.lunit)
        pX = float(self.pX)*uval/2.0
        pY = float(self.pY)*uval/2.0
        pZ = float(self.pZ)*uval/2.0

        _log.info('box.pycsgmesh> mesh')
        mesh = _CSG.cube(center=[0,0,0], radius=[pX,pY,pZ])
        return mesh

