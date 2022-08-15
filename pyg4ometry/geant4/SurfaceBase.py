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
            return x
        elif isinstance(x, str):
            y = None
            if t == OpticalSurface: y = self.registry.solidDict[x]
            if t == LogicalVolume:  y = self.registry.logicalVolumeDict[x]
            if t == PhysicalVolume: y = self.registry.physicalVolumeDict[x]
            if y == None:
                raise ValueError(f"{str(t)} not found in the registry!")
            return y
        raise ValueError(f"Unsupported type for {p}: {type(x)}")
