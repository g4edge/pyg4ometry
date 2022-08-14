from .solid.OpticalSurface import OpticalSurface
from .LogicalVolume import LogicalVolume
from .PhysicalVolume import PhysicalVolume

class SurfaceBase:
    def __init__(self, name, type, surface_property, registry, addRegistry):
        self.name = name
        self.type = type
        self.registry = registry
        self.surface_property = self._chkType(surface_property, OpticalSurface, "surface_property")

        if addRegistry:
            registry.addSurface(self)

    def _chkType(self, x, t, p):
        if isinstance(x, t):
            if t == OpticalSurface: assert(x in self.registry.solidDict.values())
            if t == LogicalVolume:  assert(x in self.registry.logicalVolumeDict.values())
            if t == PhysicalVolume: assert(x in self.registry.physicalVolumeDict.values())
            return x.name
        elif isinstance(x, str):
            return x
        raise ValueError(f"Unsupported type for {p}: {type(x)}")
