from collections import OrderedDict, MutableMapping
from itertools import count
import logging

import pyg4ometry.geant4 as _g4
from .region import Region
from .directive import RecursiveRotoTranslation, RotoTranslation
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
        self.bodyDict = OrderedDict()
        self.rotoTranslationsDict = RotoTranslationStore()
        self.regionDict = OrderedDict()
        self.materialDict = OrderedDict()
        self.latticeDict = OrderedDict()
        self.cardDict = OrderedDict()

        self._bodiesAndRegions = {}

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise IdenticalNameError(body.name)
        logger.debug("%s", body)
        self.bodyDict[body.name] = body

    def addRotoTranslation(self, rototrans):
        self.rotoTranslationsDict.addRotoTranslation(rototrans)

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

    def getNonLatticeRegions(self):
        out = {}
        for name, region in self.regionDict.iteritems():
            if name in self.latticeDict:
                continue
            out[name] = region
        return out

class RotoTranslationStore(MutableMapping):
    """ only get by names."""
    def __init__(self):
        self._nameMap = OrderedDict()
        # internal infinite counter generating new unique
        # transformation indices.
        self._counter = count(start=2000, step=1000)

    def __getitem__(self, name):
        return self._nameMap[name]

    # def __repr__(self):
    #     return repr(self._nameMap).replace

    def __setitem__(self, name, rtrans):
        if not isinstance(rtrans, (RotoTranslation, RecursiveRotoTranslation)):
            msg = "Only store RotoTranslation or RecursiveRotoTranslation."
            raise TypeError(msg)
        if name != rtrans.name:
            raise ValueError("Name it is appended with doesn't match"
                             " the name of the RotoTranslation instance...")

        # If already defined then we give it the same transformation
        # index as the one we are overwriting.
        if name in self._nameMap:
            rtrans.transformationIndex = self._nameMap[name].transformationIndex
        self._nameMap[name] = rtrans

    def addRotoTranslation(self, rtrans):
        name = rtrans.name
        if name in self: # match the name to the previous transformationIndex
            rtrans.transformationIndex = self[name].transformationIndex
            self[name].append(rtrans)
        else:
            # Insert as a RecursiveRotoTranslation to make any future
            # adding of RotoTranslations easier.
            recur = RecursiveRotoTranslation(name, [rtrans])
            if not rtrans.transformationIndex:
                recur.transformationIndex = next(self._counter)
            elif rtrans.transformationIndex in self.allTransformationIndices():
                raise KeyError("transformation index matches another"
                               " ROT-DEFI with a different name.  Change the"
                               " transformationIndex and try again.")
            elif rtrans.transformationIndex not in self.allTransformationIndices():
                pass #
            self[name] = recur

    def allTransformationIndices(self):
        return [rtrans.transformationIndex for rtrans in self.values()]

    def __delitem__(self, key):
        del self._nameMap[key]

    def __iter__(self):
        return iter(self._nameMap)

    def __len__(self):
        return len(self._nameMap)

    def flukaFreeString(self):
        return "\n".join([r.flukaFreeString() for r in self.values()])
