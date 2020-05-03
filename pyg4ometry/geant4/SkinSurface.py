
class SkinSurface:
    def __init__(self, name, volumeref, surface_property, registry, addRegistry=True):
        self.name = name
        self.type = 'skinsurface'
        self.volumeref = volumeref
        self.surface_property = surface_property

        if addRegistry:
            registry.addSurface(self)

    def __repr__(self):
        return 'SkinSurface {} : volref {}'.format(self.name, self.volumeref)
