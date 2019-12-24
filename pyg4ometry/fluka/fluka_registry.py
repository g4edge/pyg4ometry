from collections import OrderedDict as _OrderedDict
import logging

import pyg4ometry.geant4 as _g4
from .region import Region
from pyg4ometry.exceptions import IdenticalNameError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FlukaRegistry(object):

    '''
    Object to store geometry for FLUKA input and output. All of the FLUKA classes \
    can be used without storing them in the Registry. The registry is used to write \
    the FLUKA output file.
    '''

    def __init__(self) :
        self.bodyDict          = _OrderedDict()
        self.bodyTransformDict = _OrderedDict()
        self.regionDict        = _OrderedDict()
        self.materialDict      = _OrderedDict()
        self.latticeDict       = _OrderedDict()
        self.cardDict          = _OrderedDict()

        self._bodiesAndRegions = {}

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise IdenticalNameError(body.name)
        logger.debug("%s", body)
        self.bodyDict[body.name] = body

    def addBodyTransform(self, trans):
        self.bodyTransformDict[trans.name] = trans

    def addRegion(self, region, addBodies=False):
        # Always build a map of bodies to regions, which we need for
        for body in region.bodies():
            if body.name in self._bodiesAndRegions:
                self._bodiesAndRegions[body.name].add(region.name)
            else:
                self._bodiesAndRegions[body.name] = {region.name}

        self.regionDict[region.name] = region

    def addMaterial(self, material):
        self.materialDict.add(material)

    def addLattice(self, lattice):
        self.latticeDict.add(lattice)

    def getBody(self, name):
        return self.bodyDict[name]

    def getBodyToRegionsMap(self):
        return self._bodiesAndRegions

    def printDefinitions(self):
        print "bodyDict = {}".format(self.bodyDict)
        print "bodyTransformDict = {}".format(self.bodyTransformDict)
        print "regionDict = {}".format(self.regionDict)
        print "materialDict = {}".format(self.materialDict)
        print "latticeDict = {}".format(self.latticeDict)
        print "cardDict = {}".format(self.cardDict)
