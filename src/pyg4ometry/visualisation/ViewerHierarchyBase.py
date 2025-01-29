from . import VisualisationOptions as _VisOptions


class ViewerHierarchyBase:
    """
    Base class for all viewers and exporters. Handles unique meshes and their instances
    """

    def __init__(self):
        self.defaultVisOptions = _VisOptions()

    def addWorld(self, worldLV):
        self.worldLV = worldLV

    def traverseHierarchy(self, LV=None):
        if not LV:
            LV = self.worldLV

        print(LV.name)

        for daughter in LV.daughterVolumes:
            self.traverseHierarchy(daughter.logicalVolume)

    def getVisOptions(self, pv):
        """
        Return a set of vis options according to the precedence of pv, lv, default.
        """
        # take the first non-None set of visOptions
        orderOfPrecedence = [pv.visOptions, pv.logicalVolume.visOptions, self.defaultVisOptions]
        return next(item for item in orderOfPrecedence if item is not None)

    def getVisOptionsLV(self, lv):
        """
        Return a set of vis options according to the precedence of lv, default.
        """
        # take the first non-None set of visOptions
        orderOfPrecedence = [lv.visOptions, self.defaultVisOptions]
        return next(item for item in orderOfPrecedence if item is not None)
