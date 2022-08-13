
class SkinSurface:
    def __init__(self, name, volumeref, surface_property, registry, addRegistry=True):
        """
        :param name: of the skin surface
        :type name: str
        :param volumeref: name of the enclosed logical volume
        :type volumeref: str
        :param surface_property: name of the referenced :code:`pyg4ometry.solid.OpticalSurface`
        :type surface_property: str
        """
        self.name = name
        self.type = 'skinsurface'
        self.volumeref = volumeref
        self.surface_property = surface_property

        if addRegistry:
            registry.addSurface(self)

    def __repr__(self):
        return 'SkinSurface {} : volref {}'.format(self.name, self.volumeref)
