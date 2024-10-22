class ViewerHierarchyBase:
    """
    Base class for all viewers and exporters. Handles unique meshes and their instances
    """

    def __init__(self):
        pass

    def addWorld(self, worldLV):
        self.worldLV = worldLV

    def traverseHierarchy(self, LV=None):
        if not LV:
            LV = self.worldLV

        print(LV.name)

        for daughter in LV.daughterVolumes:
            self.traverseHierarchy(daughter.logicalVolume)
