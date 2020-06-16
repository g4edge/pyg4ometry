import pickle
from collections import OrderedDict, MutableMapping
from itertools import count
import logging

import numpy as np
import pandas as pd
import pyg4ometry.geant4 as _g4
from .region import Region
from .directive import RecursiveRotoTranslation, RotoTranslation
from pyg4ometry.exceptions import IdenticalNameError
from .material import (defineBuiltInFlukaMaterials,
                       BuiltIn,
                       predefinedMaterialNames)
from . import body as _body

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FlukaRegistry(object):
    '''
    Object to store geometry for FLUKA input and output. All of the FLUKA classes \
    can be used without storing them in the Registry. The registry is used to write \
    the FLUKA output file.
    '''

    def __init__(self) :
        self.bodyDict = FlukaBodyStore()
        self.rotoTranslations = RotoTranslationStore()
        self.regionDict = OrderedDict()
        self.materials = OrderedDict()
        self.latticeDict = OrderedDict()
        self.cardDict = OrderedDict()
        self.assignmas = OrderedDict()
        self._predefinedMaterialNames = set(predefinedMaterialNames())

        # Instantiate the predefined materials as BuiltIn instances
        defineBuiltInFlukaMaterials(self)

        self._bodiesAndRegions = {}

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise IdenticalNameError(body.name)
        logger.debug("%s", body)
        self.bodyDict[body.name] = body

    def makeBody(self, *args, **kwargs):
        return self.bodyDict.make(*args, **kwargs)

    def addRotoTranslation(self, rototrans):
        self.rotoTranslations.addRotoTranslation(rototrans)

    def addRegion(self, region, addBodies=False):
        # Always build a map of bodies to regions, which we need for
        for body in region.bodies():
            if body.name in self._bodiesAndRegions:
                self._bodiesAndRegions[body.name].add(region.name)
            else:
                self._bodiesAndRegions[body.name] = {region.name}

        self.regionDict[region.name] = region

    def addLattice(self, lattice):
        if lattice.cellRegion.name in self.regionDict:
            raise ValueError(
                "LATTICE cell already been defined as a region in regionDict")
        self.latticeDict[lattice.cellRegion.name] = lattice

    def getBody(self, name):
        return self.bodyDict[name]

    def getBodyToRegionsMap(self):
        return self._bodiesAndRegions

    def printDefinitions(self):
        print("bodyDict = {}".format(self.bodyDict))
        print("regionDict = {}".format(self.regionDict))
        print("materialDict = {}".format(self.materials))
        print("latticeDict = {}".format(self.latticeDict))
        print("cardDict = {}".format(self.cardDict))

    def regionAABBs(self, write=None):
        regionAABBs = {}
        for regionName, region in self.regionDict.items():
            regionAABBs[regionName] = region.extent()

        if write:
            with open(write, "wb") as f:
                pickle.dump(regionAABBs, f)

        return regionAABBs

    def latticeAABBs(self):
        latticeCellAABBs = {}
        for cellName, lattice in self.latticeDict.items():
            latticeCellAABBs[cellName] = lattice.cellRegion.extent()
        return latticeCellAABBs

    def addMaterial(self, material):
        name = material.name
        # Only allow redefinition of builtins..  anything else is
        # almost certainly not deliberate.
        if name in self.materials and name not in self._predefinedMaterialNames:
            raise IdenticalNameError(name)
        self.materials[material.name] = material

    def getMaterial(self, name):
        return self.materials[name]

    def addMaterialAssignments(self, mat, *regions):
        if isinstance(mat, Region):
            raise TypeError("A Region instance has been provided as a material")

        try: # Element or Compound instance
            materialName = mat.name
        except AttributeError: # By name, get Ele/Comp from self.
            materialName = mat
            mat = self.materials[materialName]
        # More checks.
        if materialName not in self.materials:
            self.addMaterialAssignments(material)
        elif mat not in self.materials.values():
            msg = ("Mismatch between provided FLUKA material \"{}\" for "
                   "assignment and existing found in registry".format(mat.name))
            raise FLUKAError(msg)

        for region in regions:
            # Either region name or Region instance
            try:
                name = region.name
            except AttributeError:
                name = region

            self.assignmas[name] = materialName

    def assignma(self, material, *regions):
        return self.addMaterialAssignments(material, *regions)


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


class FlukaBodyStore(MutableMapping):
    def __init__(self):
        self._bodies = {} # bodies that aren't half spaces.
        self._df = pd.DataFrame({"name": [],
                                 "body": [],
                                 "planeNormal": [],
                                 "pointOnPlane": []})

    def make(self, clas, *args, **kwargs):
        try:
            del kwargs["flukaregistry"] # Prevent infinite recursion
        except KeyError:
            pass

        if clas in {_body.XZP, _body.YZP, _body.XYP, _body.PLA}:
            return self._makeHalfSpace(clas, *args, **kwargs)
        else:
            body = clas(*args, **kwargs)
            self._bodies[_body.name] = body
            return body

    def _makeHalfSpace(self, clas, *args, **kwargs):
        body = clas(*args, **kwargs)
        normal, point = body.toPlane()

        if not self:
            self[body.name] = body
            return body

        mask = self._getMaskHalfSpace(body)
        if sum(mask) == 0: # I.e. this half space has not been defined before.
            return body

        return self._df[mask]["body"].item()

    def _getMaskHalfSpace(self, body):
        normal, point = body.toPlane()
        return self._maskHelper(["planeNormal", "pointOnPlane"],
                                [normal, point])

    def _maskHelper(self, columns, values):
        mask = np.full_like(self._df["name"], True, dtype=bool)
        for col, value in zip(columns, values):
            mask &= self._df[col].apply(
                    lambda x, value=value: np.isclose(x, value).all())
        return mask

    def _addHalfSpaceToDF(self, body):
        name = body.name
        normal, point = body.toPlane()
        df = pd.DataFrame(
            [[name, np.array(normal), np.array(point), body]],
            columns=["name", "planeNormal",
                     "pointOnPlane", "body"]
        )
        self._df.loc[len(self._df.index)] = df.iloc[0]

    def addBody(self, body):
        s = self._getStore(body)
        s[body.name] = body

    def __setitem__(self, key, value):
        self._bodies[key] = value
        if isinstance(value, (_body.XZP, _body.YZP, _body.XYP, _body.PLA)):
            self._addHalfSpaceToDF(value)

    def __getitem__(self, key):
        return self._bodies[key]

    def __delitem__(self, key):
        del self._bodies[key]
        if key in self._df["name"]:
            from IPython import embed; embed()
            rowIndex = df[df["name"] == key].index
            self._df.drop(rowIndex, inplace=True)

    def __len__(self):
        return len(self._bodies)

    def __contains__(self, key):
        return key in self._bodies

    def __iter__(self):
        return iter(self._bodies)
