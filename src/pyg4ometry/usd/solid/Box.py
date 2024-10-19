from pxr import Usd, UsdGeom, Sdf, Gf
from .SolidBase import SolidBase


class Box(SolidBase):
    # Custom class inheriting from UsdGeom.Xform

    def __init__(self, stage, path):
        super().__init__(stage, path)
        self.SetCustomFloatAttribute("x", 1)
        self.SetCustomFloatAttribute("y", 1)
        self.SetCustomFloatAttribute("z", 1)

    @staticmethod
    def Define(stage, path):
        """
        Define a new Geant4 Box on the USD stage at the given path.
        """
        prim = stage.DefinePrim(path, "Mesh")  # Inherits Xform
        return Box(stage, path)
