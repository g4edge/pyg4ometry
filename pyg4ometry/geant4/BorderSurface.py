
class BorderSurface:
    def __init__(self, name, physref1, physref2, surface_property, registry, addRegistry=True):
        self.name = name
        self.type = 'bordersurface'
        self.surface_property  = surface_property
        self.physref1 = physref1
        self.physref2 = physref2

        if addRegistry:
            registry.addSurface(self)

    def __repr__(self):
        return 'BorderSurface {} : physvol  {}, {}'.format(self.name, self.physref1, self.physref2)
