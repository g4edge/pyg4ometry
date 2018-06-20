from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry

class OpticalSurface(_SolidBase):
    def __init__(self, name, osfinish, model, type, value, register=True):
        self.name   = name
        self.type   = 'opticalsurface'
        self.finish = osfinish
        self.model  = model
        self.osType = type
        self.value  = value
        if register:
            _registry.addSolid(self)


    def __repr__(self):
        return 'OpticalSurface : '+str(self.name)
