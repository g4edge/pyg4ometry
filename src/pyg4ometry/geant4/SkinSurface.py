from .LogicalVolume import LogicalVolume
from .SurfaceBase import SurfaceBase

class SkinSurface(SurfaceBase):
    def __init__(self, name, volumeref, surface_property, registry, addRegistry=True):
        """
        :param name: of the skin surface
        :type name: str
        :param volumeref: the enclosed logical volume
        :type volumeref: str,LogicalVolume
        :param surface_property: the referenced :code:`pyg4ometry.solid.OpticalSurface`
        :type surface_property: str,OpticalSurface
        """
        super(SkinSurface, self).__init__(name, 'skinsurface', surface_property, registry, addRegistry)

        self.volumeref = self._chkType(volumeref, LogicalVolume, 'volumeref')

    def __repr__(self):
        return 'SkinSurface {} : volref {}'.format(self.name, self.volumeref)
