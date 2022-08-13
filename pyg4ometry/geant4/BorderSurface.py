
class BorderSurface:
    def __init__(self, name, physref1, physref2, surface_property, registry, addRegistry=True):
        """
        :param name: of the border surface
        :type name: str
        :param physref1: name of the first physical volume of this surface
        :type physref1: str
        :param physref2: name of the second physical volume of this surface
        :type physref2: str
        :param surface_property: name of the referenced :code:`pyg4ometry.solid.OpticalSurface`
        :type surface_property: str
        """
        self.name = name
        self.type = 'bordersurface'
        self.surface_property  = surface_property
        self.physref1 = physref1
        self.physref2 = physref2

        if addRegistry:
            registry.addSurface(self)

    def __repr__(self):
        return 'BorderSurface {} : physvol  {}, {}'.format(self.name, self.physref1, self.physref2)
