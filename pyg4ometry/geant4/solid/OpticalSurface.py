from .SolidBase import SolidBase as _SolidBase

class OpticalSurface(_SolidBase):

    allowed_models    = []
    allowed_types     = []
    allowed_finishes  = []

    def __init__(self, name, finish, model, surf_type, value, registry, addRegistry=True):
        super(OpticalSurface, self).__init__(name, 'OpticalSurface', registry)
        self.finish = finish
        self.model  = model
        self.osType = surf_type
        self.value  = value
        self.properties = {}

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return 'OpticalSurface : '+str(self.name)

    def addProperty(self, name, value) : 
        self.properties[name] = value
