from .Surfaces import BOX as _BOX
from .Surfaces import RPP as _RPP
from .Surfaces import RCC as _RCC
from .Surfaces import RHP_HEX as _RHP_HEX
from .Surfaces import REC as _REC
from .Surfaces import TRC as _TRC
from .Surfaces import WED as _WED
from .Surfaces import ARB as _ARB


class Registry:
    def __init__(self):
        self.surfaceDict = {}
        self.transformationDict = {}
        self.materialDict = {}
        self.cellDict = {}

    def addSurface(self, surface):
        if surface.surfaceNumber in self.surfaceDict:
            surface.surfaceNumber = self.getNewSurfaceNumber()
        if not surface.surfaceNumber:
            surface.surfaceNumber = self.getNewSurfaceNumber()
        self.surfaceDict[surface.surfaceNumber] = surface

        if type(surface) is _BOX:
            self.addSubsurface(surface, 6)

        if type(surface) is _RPP:
            self.addSubsurface(surface, 6)

        # SPH treated as regular surface

        if type(surface) is _RCC:
            self.addSubsurface(surface, 3)

        if type(surface) is _RHP_HEX:
            self.addSubsurface(surface, 8)

        if type(surface) is _REC:
            self.addSubsurface(surface, 3)

        if type(surface) is _TRC:
            self.addSubsurface(surface, 3)

        # ELL treated as regular surface

        if type(surface) is _WED:
            self.addSubsurface(surface, 5)

        if type(surface) is _ARB:
            self.addSubsurface(surface, 6)

    def addSubsurface(self, surface, numToAdd):
        for i in range(1, numToAdd + 1, 1):
            self.surfaceDict[str(surface.surfaceNumber) + "." + str(i)] = surface

    def addCell(self, cell):
        if cell.cellNumber in self.cellDict:
            cell.cellNumber = self.getNewCellNumber()
        if not cell.cellNumber:
            cell.cellNumber = self.getNewCellNumber()
        self.cellDict[cell.cellNumber] = cell

    def addTransformation(self, transformation):
        if transformation.transformationNumber in self.transformationDict:
            transformation.transformationNumber = self.getNewTransformationNumber()
        if not transformation.transformationNumber:
            transformation.transformationNumber = self.getNewTransformationNumber()
        self.transformationDict[transformation.transformationNumber] = transformation

    def addMaterial(self):
        pass
        # todo

    def getNewSurfaceNumber(self):
        if len(self.surfaceDict.keys()) == 0:
            return 1
        return max(self.surfaceDict.keys()) + 1

    def getNewCellNumber(self):
        if len(self.cellDict.keys()) == 0:
            return 1
        return max(self.cellDict.keys()) + 1

    def getNewTransformationNumber(self):
        if len(self.transformationDict.keys()) == 0:
            return 1
        return max(self.transformationDict.keys()) + 1
