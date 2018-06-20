from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ..Registry import registry as _registry

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
    def __init__(self, name='', pX=0.0, pY=0.0, pZ=0.0, register=True):
        self.name = name
        self.pX = pX
        self.pY = pY
        self.pZ = pZ
        self.type = 'Box'
        self.mesh = None
        if register:
            _registry.addSolid(self)

    def __repr__(self):
        return 'Box : '+self.name+' '+str(self.pX)+' '+str(self.pY)+' '+str(self.pZ)

    def pycsgmesh(self):
        self.mesh = _CSG.cube(center=[0,0,0], radius=[float(self.pX),float(self.pY),float(self.pZ)])
        return self.mesh
