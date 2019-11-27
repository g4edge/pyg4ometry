from collections import OrderedDict as _OrderedDict
import pyg4ometry.geant4 as _g4
from pyg4ometry.exceptions import IdenticalNameError


class FlukaRegistry(object):
    def __init__(self) :
        self.bodyDict          = _OrderedDict()
        self.bodyTransformDict = _OrderedDict()
        self.regionDict        = _OrderedDict()
        self.materialDict      = _OrderedDict()
        self.latticeDict       = _OrderedDict()
        self.cardDict          = _OrderedDict()

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise IdenticalNameError(body.name)
        self.bodyDict[body.name] = body

    def addBodyTransform(self, trans):
        self.bodyTransformDict[trans.name] = trans

    def addRegion(self, region):
        self.regionDict[region.name] = region

    def addMaterial(self, material):
        self.materialDict.add(material)

    def addLattice(self, lattice):
        self.latticeDict.add(lattice)

    def getBody(self, name):
        return self.bodyDict[name]

    def printDefinitions(self):
        print "bodyDict = {}".format(self.bodyDict)
        print "bodyTransformDict = {}".format(self.bodyTransformDict)
        print "regionDict = {}".format(self.regionDict)
        print "materialDict = {}".format(self.materialDict)
        print "latticeDict = {}".format(self.latticeDict)
        print "cardDict = {}".format(self.cardDict)

    def toG4Registry(self):
        greg = _g4.Registry()

        wm = _g4.MaterialPredefined("G4_Galactic")

        ws = _g4.solid.Box("ws", 100, 100, 100, greg, "mm")
        wlv = _g4.LogicalVolume(ws, wm, "wl", greg)

        for name, region in self.regionDict.iteritems():
            s = region.geant4_solid(greg)
            bm = _g4.MaterialPredefined("G4_Fe")
            rlv = _g4.LogicalVolume(s, bm, name+"bl", greg)

            rpv = _g4.PhysicalVolume(list(region.tbxyz()),
                                     list(region.centre()),
                                     rlv, "b_pv1", wlv, greg)

        greg.setWorld(wlv.name)
        return greg
