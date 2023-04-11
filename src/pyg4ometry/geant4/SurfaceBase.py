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

    def _chkType(self, obj, t, prop):
        if isinstance(obj, t):
            return obj
        elif isinstance(obj, str):
            instance = None
            if t == OpticalSurface: instance = self.registry.solidDict[obj]
            if t == LogicalVolume:  instance = self.registry.logicalVolumeDict[obj]
            if t == PhysicalVolume: instance = self.registry.physicalVolumeDict[obj]
            if instance == None:
                raise ValueError(f"{str(t)} {x} not found in the registry!")
            return instance
        raise ValueError(f"Unsupported type for {prop}: {type(obj)}")
