from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.geant4.Registry import registry as _registry

class Box(_SolidBase) :
    '''
    Constructs a box. 
    
    Inputs:
        name:   string, name of the volume
        pX:     float, half-length along x
        pY:     float, half-length along y
        pZ:     float, half-length along z
    '''

    def __init__(self, name = '', pX = 0.0, pY = 0.0, pZ = 0.0) :
        self.name = name
        self.pX = pX
        self.pY = pY
        self.pZ = pZ
        self.type = 'Box'
        self.mesh = None
        if name != '' :
            _registry.addSolid(self)

    def __repr__(self):
        return 'Box : '+self.name+' '+str(self.pX)+' '+str(self.pY)+' '+str(self.pZ)

    def pycsgmesh(self):
        self.mesh = _CSG.cube(center=[0,0,0], radius=[float(self.pX),float(self.pY),float(self.pZ)])
        return self.mesh
