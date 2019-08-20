from collections import OrderedDict as _OrderedDict

class FlukaRegistry:
    def __init__(self) :
        self.bodyDict          = _OrderedDict()
        self.bodyTransformDict = _OrderedDict()
        self.regionDict        = _OrderedDict()
        self.materialDict      = _OrderedDict()
        self.latticeDict       = _OrderedDict()
        self.cardDict          = _OrderedDict()

    def addBody(self, body):
        self.bodyDict[body.name] = body

    def addRegion(self, region):
        self.regionDict.add(region)

    def addMaterial(self, material):
        self.materialDict.add(material)

    def addLattice(self, lattice):
        self.latticeDict.add(lattice)

