import sys as _sys
from collections import OrderedDict as _OrderedDict
if _sys.version_info < (3, 10):
    from collections import MutableMapping as _MutableMapping
else:
    from collections.abc import MutableMapping as _MutableMapping

from itertools import count as _count

import numpy as _np
import pandas as _pd
import pyg4ometry.geant4 as _g4
from .region import Region as _Region
from .directive import RecursiveRotoTranslation as _RecursiveRotoTranslation
from .directive import RotoTranslation as _RotoTranslation
from pyg4ometry.exceptions import IdenticalNameError as _IdenticalNameError
from pyg4ometry.exceptions import FLUKAError as _FLUKAError
from .material import (defineBuiltInFlukaMaterials,
                       BuiltIn,
                       predefinedMaterialNames)
from . import body as _body
from . import vector as _vector
from . import card as _card

import logging as _logging
logger = _logging.getLogger(__name__)
logger.setLevel(_logging.INFO)

class FlukaRegistry(object):
    """
    Object to store geometry for FLUKA input and output. All of the FLUKA classes \
    can be used without storing them in the Registry. The registry is used to write \
    the FLUKA output file.
    """
    def __init__(self):
        self.bodyDict = FlukaBodyStore()
        self.rotoTranslations = RotoTranslationStore()
        self.regionDict = _OrderedDict()
        self.materials = _OrderedDict()
        self.latticeDict = _OrderedDict()
        self.cardDict = _OrderedDict()
        self.assignmas = _OrderedDict()
        self._predefinedMaterialNames = set(predefinedMaterialNames())

        # Instantiate the predefined materials as BuiltIn instances
        defineBuiltInFlukaMaterials(self)

        self._bodiesAndRegions = {}

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise _IdenticalNameError(body.name)
        logger.debug("%s", body)
        self.bodyDict[body.name] = body

    def makeBody(self, clas, *args, **kwargs):
        return self.bodyDict.make(clas, *args, **kwargs)

    def getDegenerateBody(self, body):
        return self.bodyDict.getDegenerateBody(body)

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
            import pickle
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
            raise _IdenticalNameError(name)
        self.materials[material.name] = material

    def getMaterial(self, name):
        return self.materials[name]

    def addMaterialAssignments(self, mat, *regions):
        if isinstance(mat, _Region):
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
            raise _FLUKAError(msg)

        for region in regions:
            # Either region name or Region instance
            try:
                name = region.name
            except AttributeError:
                name = region

            self.assignmas[name] = materialName

    def assignma(self, material, *regions):
        return self.addMaterialAssignments(material, *regions)

    def addCard(self, card):
        if card.keyword in self.cardDict:
            self.cardDict[card.keyword].append(card)
        else :
            self.cardDict[card.keyword] = [card]

    def addGlobal(self):
        pass

    def addDefaults(self):
        pass

    def addBeam(self):
        pass

    def addBeamPos(self):
        pass

    def addUserBin(self):
        pass

    def addUsrBdx(self, binning, scoringDir, scoringType, type, lunOutput, reg1, reg2, area, name,
                   maxKE = None,minKE = None, nKEbin = None, maxSA = None, minSA = None, nSEbin = None):
        c1 = _card.Card("USRBDX",binning + 10*scoringDir + 100*scoringType, type, lunOutput, reg1, reg2, area, name)
        c2 = _card.Card("USRBDX",maxKE, minKE, nKEbin, maxSa, minSA, nSEbin, "&")

        self.addCard(c1)
        self.addCard(c2)

    def addUsricall(self):
        pass

    def addUsrocall(self):
        pass

    def addUserDump(self, mgdraw = 100, lun=70, mgdrawOpt=-1, what4=0, sdum=None):
        if not sdum :
            c = _card.Card("USERDUMP",mgdraw, lun, mgdrawOpt, sdum=sdum)
            self.addCard(c)
        elif sdum == "UDQUENCH" :
            c1 = _card.Card()

    def assddRandomiz(self, seedLun =1, seed=54217137):
        c = _card.Card("RANDOMIZ", seedLun, seed)
        self.addCard(c)

    def addStart(self, maxPrimHistories, timeTermSec= None, coreDump = None, eachHistoryOutput = None):
        c = _card.Card("START", maxPrimHistories,None,timeTermSec,coreDump,eachHistoryOutput)
        self.addCard(c)

class RotoTranslationStore(_MutableMapping):
    """ only get by names."""
    def __init__(self):
        self._nameMap = _OrderedDict()
        # internal infinite counter generating new unique
        # transformation indices.
        self._counter = _count(start=2000, step=1000)

    def __getitem__(self, name):
        return self._nameMap[name]

    # def __repr__(self):
    #     return repr(self._nameMap).replace

    def __setitem__(self, name, rtrans):
        if not isinstance(rtrans, (_RotoTranslation, _RecursiveRotoTranslation)):
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
            recur = _RecursiveRotoTranslation(name, [rtrans])
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


class FlukaBodyStore(_MutableMapping):
    def __init__(self):
        self._df = _pd.DataFrame()
        hscacher = HalfSpaceCacher(self._df)
        infCylCacher = InfiniteCylinderCacher(self._df)

        self._cachers = {_body.XZP: hscacher,
                         _body.YZP: hscacher,
                         _body.XYP: hscacher,
                         _body.PLA: hscacher,
                         _body.XCC: infCylCacher,
                         _body.YCC: infCylCacher,
                         _body.ZCC: infCylCacher
        }
        self._basecacher = BaseCacher(self._df)

    def _bodyNames(self):
        return list(self._df["name"])

    def _bodies(self):
        return list(self._df["body"])

    def _getCacherFromBody(self, body):
        return self._cachers.get(type(body), self._basecacher)

    def make(self, clas, *args, **kwargs):
        try:
            del kwargs["flukaregistry"] # Prevent infinite recursion
        except KeyError:
            pass
        try:
            result =  self._cachers[clas].make(clas, *args, **kwargs)
            return result

        except KeyError:
            return self._basecacher.make(clas, *args, **kwargs)

    def getDegenerateBody(self, body):
        return self._getCacherFromBody(body).getDegenerateBody(body)

    def addBody(self, body):
        self[body.name] = body

    def __setitem__(self, key, value):
        assert key == value.name
        c = self._getCacherFromBody(value)
        c.setBody(value)

    def __getitem__(self, key):
        if key not in self._bodyNames():
            raise _FLUKAError(f"Undefined body: {key}")
        return self._df[self._df["name"] == key]["body"].item()

    def __delitem__(self, key):
        if key not in self._bodyNames():
            raise KeyError(f"Missing body name: {key}")

        body = self[key]
        self._getCacherFromBody(body).remove(key)

    def __len__(self):
        return len(self._df)

    def __contains__(self, key):
        return key in self._bodyNames()

    def __iter__(self):
        return iter(self._bodyNames())

    def __repr__(self):
        return repr(dict(zip(self._bodyNames(), self._bodies())))

class BaseCacher:
    COLUMNS =  ["name", "body"]
    def __init__(self, df):
        self.df = df
        for column in self.COLUMNS:
            try:
                self.df.insert(len(self.df), column, [])
            except ValueError: # already added the column maybe
                pass

    def appendData(self, variables):
        df = _pd.DataFrame([variables], columns=self.COLUMNS)
        self.df.loc[len(self.df.index)] = df.iloc[0]

    def append(self, body):
        name = body.name
        df = _pd.DataFrame([[name, body]], columns=self.COLUMNS)
        self.df.loc[len(self.df.index)] = df.iloc[0]

    def setBody(self, body):
        name = body.name
        if name not in self.df["name"]:
            self.append(body)
        else:
            rowIndex= self.df[self.df["name"] == name].index
            raise NotImplementedError("operation not implemented")

    def addBody(self, body):
        name = body.name
        df = _pd.DataFrame([[name, body]], columns=self.COLUMNS)
        self.df.loc[len(self.df.index)] = df.iloc[0]

    def remove(self, key):
        rowIndex = self.df[self.df["name"] == key].index
        self.df.drop(rowIndex, inplace=True)

    def make(self, clas, *args, **kwargs):
        body = clas(*args, **kwargs)
        return self.getDegenerateBody(body)

    def getDegenerateBody(self, body):
        self.append(body)
        return body

    def __repr__(self):
        return f"<{type(self).__name__}>"


class Cacheable(BaseCacher):
    def getDegenerateBody(self, body):
        mask = self.mask(body)
        if not mask.any(): # i.e. this half space has not been defined before.
            self.append(body)
            return body
        result = self.df[mask]["body"].item()
        return result # self.df[mask]["body"].item()

    def getMask(self, columns, values, predicates):
        if self.df.empty:
            return _np.array([], dtype=bool)
        mask = _np.full_like(self.df["name"], True, dtype=bool)
        for column, value, predicate in zip(columns, values, predicates):
            mask &= self.df[column].apply(
                lambda x, value=value, predicate=predicate: predicate(
                    x, _np.array(value)
                ).all()
            )
        return mask


class HalfSpaceCacher(Cacheable):
    COLUMNS = ["name", "body", "planeNormal", "pointOnPlane"]
    def append(self, body):
        name = body.name
        normal, point = body.toPlane()
        super().appendData([name, body, _np.array(normal), _np.array(point)])

    def mask(self, body):
        normal, point = body.toPlane()
        return self.getMask(["planeNormal", "pointOnPlane"],
                            [normal, point],
                            [_np.isclose, _np.isclose])


class InfiniteCylinderCacher(Cacheable):
    COLUMNS = ["name", "body", "direction", "pointOnLine", "radius"]
    def append(self, body):
        super().appendData(
            [body.name,
             body,
             body.direction(),
             self._cylinderPoint(body),
             body.radius]
        )

    def mask(self, body):
        return self.getMask(
            ["direction", "pointOnLine", "radius"],
            [body.direction(), self._cylinderPoint(body), body.radius],
            [_vector.areParallelOrAntiParallel, _np.isclose, _np.isclose])

    @staticmethod
    def _cylinderPoint(body):
        return _vector.pointOnLineClosestToPoint([0, 0, 0],
                                                 body.point(),
                                                 body.direction())
