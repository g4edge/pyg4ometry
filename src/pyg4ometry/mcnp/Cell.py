class Cell:
    def __init__(self, reg=None, cellNumber=None):
        self.surfaceList = []
        self.cellNumber = cellNumber
        if reg:
            reg.addCell(self)

    def addSurface(self, surface):
        self.surfaceList.append(surface)
