from SolidBase import SolidBase as _SolidBase
from pyg4ometry.pycsg.core import CSG as _CSG

import logging as _log

class Box(_SolidBase):
    """
    Constructs a box.

    :param name: of object in registry
    :type name: str
    :param pX: half-length along x
    :type name: float
    :param pY: half-length along y
    :type name: float
    :param pZ: half-length along z
    :type name: float
    """

    def __init__(self, name='', pX=0.0, pY=0.0, pZ=0.0, registry=None):
        self.name = name
        self.pX = pX
        self.pY = pY
        self.pZ = pZ
        self.type = 'Box'
        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return 'Box : '+self.name+' '+str(self.pX)+' '+str(self.pY)+' '+str(self.pZ)

    def pycsgmesh(self):
        _log.info('box.pycsgmesh> antlr')

        pX = float(self.pX)
        pY = float(self.pY)
        pZ = float(self.pZ)

        _log.info('box.pycsgmesh> mesh')
        mesh = _CSG.cube(center=[0,0,0], radius=[pX,pY,pZ])
        return mesh

