from .PhysicalVolume import PhysicalVolume
from .SurfaceBase import SurfaceBase

class BorderSurface(SurfaceBase):
    def __init__(self, name, physref1, physref2, surface_property, registry, addRegistry=True):
        """
        :param name: of the border surface
        :type name: str
        :param physref1: the first physical volume of this surface
        :type physref1: str,PhysicalVolume
        :param physref2: the second physical volume of this surface
        :type physref2: str,PhysicalVolume
        :param surface_property: the referenced :class:`pyg4ometry.solid.OpticalSurface`
        :type surface_property: str,OpticalSurface
        """
        super(BorderSurface, self).__init__(name, 'bordersurface', surface_property, registry, addRegistry)

        self.physref1 = self._chkType(physref1, PhysicalVolume, 'physref1')
        self.physref2 = self._chkType(physref2, PhysicalVolume, 'physref2')

    def __repr__(self):
        return 'BorderSurface {} : physvol  {}, {}'.format(self.name, self.physref1, self.physref2)
