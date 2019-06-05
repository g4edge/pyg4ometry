from SolidBase import SolidBase as _SolidBase

class OpticalSurface(_SolidBase):

    allowed_models    = []
    allowed_types     = []
    allowed_finishes  = []

    def __init__(self, name, finish, model, type, value, registry, addRegistry=True):
        self.name   = name
        self.type   = 'OpticalSurface'
        self.finish = finish
        self.model  = model
        self.osType = type
        self.value  = value
        if addRegistery:
            registry.addSolid(self)

        self.property = {}

    def __repr__(self):
        return 'OpticalSurface : '+str(self.name)

    def addProperty(self, name, property) : 
        self.property[name] = property
