class Registry:
    def __init__(self):
        self.surfaceDict = {}
        self.macrobodyDict = {}
        self.transformationDict = {}
        self.materialDict = {}
        self.cellDict = {}

    def addSurface(self, surface):
        if surface.surfaceNumber in self.surfaceDict:
            surface.surfaceNumber = self.getNewSurfaceNumber()
        if not surface.surfaceNumber:
            surface.surfaceNumber = self.getNewSurfaceNumber()
        self.surfaceDict[surface.surfaceNumber] = surface

    def getNewSurfaceNumber(self):
        if len(self.surfaceDict.keys()) == 0:
            return 1
        return max(self.surfaceDict.keys()) + 1

    def addCell(self, cell):
        if cell.cellNumber in self.cellDict:
            cell.cellNumber = self.getNewCellNumber()
        if not cell.cellNumber:
            cell.cellNumber = self.getNewCellNumber()
        self.cellDict[cell.cellNumber] = cell

    def getNewCellNumber(self):
        if len(self.cellDict.keys()) == 0:
            return 1
        return max(self.cellDict.keys()) + 1
