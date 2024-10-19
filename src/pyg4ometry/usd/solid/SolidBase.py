from pxr import Usd, UsdGeom, Sdf, Gf


class SolidBase(UsdGeom.Mesh):

    def __init__(self, stage, path):
        super().__init__(stage.GetPrimAtPath(path))

    def CreateCustomStingAttribute(self, name, value=""):
        """
        Set a custom float attribute on the prim.
        """
        # Create a new custom attribute if it doesn't exist
        custom_attr = self.GetPrim().CreateAttribute(name, Sdf.ValueTypeNames.String)
        custom_attr.Set(value)

    def CreateCustomFloatAttribute(self, name, value=0.0):
        """
        Set a custom float attribute on the prim.
        """
        # Create a new custom attribute if it doesn't exist
        custom_attr = self.GetPrim().CreateAttribute(name, Sdf.ValueTypeNames.Float)
        custom_attr.Set(value)

    def SetCustomAttribute(self, name, value):
        custom_attr = self.GetPrim().GetAttribute(name)
        custom_attr.Set(value)

    def GetCustomAttribute(self, name):
        """
        Get the value of a custom attribute.
        """
        custom_attr = self.GetPrim().GetAttribute(name)
        return custom_attr.Get() if custom_attr else None
