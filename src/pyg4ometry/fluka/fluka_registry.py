import sys as _sys
from collections import OrderedDict as _OrderedDict
from collections.abc import MutableMapping as _MutableMapping

import numpy as _np
import pandas as _pd
from .. import geant4 as _g4
from .region import Region as _Region
from .region import bracket_depth as _bracket_depth
from .region import bracket_number as _bracket_number
from .directive import RecursiveRotoTranslation as _RecursiveRotoTranslation
from .directive import RotoTranslation as _RotoTranslation
from .directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
from ..exceptions import IdenticalNameError as _IdenticalNameError
from ..exceptions import FLUKAError as _FLUKAError
from .material import (
    defineBuiltInFlukaMaterials,
    BuiltIn,
    predefinedMaterialNames,
    multiGroupNeutronCrossSections,
    Material,
    Compound,
)
from . import body as _body
from . import vector as _vector
from . import card as _card
from ..transformation import tbxyz2matrix as _tbxyz2matrix
from ..transformation import matrix2tbxyz as _matrix2tbxyz

import logging as _logging

logger = _logging.getLogger(__name__)
logger.setLevel(_logging.INFO)


class FlukaRegistry:
    """
    Object to store geometry for FLUKA input and output. All of the FLUKA classes \
    can be used without storing them in the Registry. The registry is used to write \
    the FLUKA output file.
    """

    def __init__(self):
        # self.bodyDict = FlukaBodyStore()
        self.bodyDict = FlukaBodyStoreExact()

        self.rotoTranslations = RotoTranslationStore()
        self.regionDict = _OrderedDict()
        self.materials = _OrderedDict()
        self.iMaterials = 0
        self.materialShortName = _OrderedDict()
        self.latticeDict = _OrderedDict()
        self.mgnFieldDict = _OrderedDict()
        self.cardDict = _OrderedDict()
        self.assignmas = _OrderedDict()
        self._predefinedMaterialNames = set(predefinedMaterialNames())

        # Instantiate the predefined materials as BuiltIn instances
        defineBuiltInFlukaMaterials(self)

        # merge indices (only used if merge functions are used)
        # B -> C, R -> S, M -> N, T->U
        self.iMerge = 0
        self.iMergeBodies = 0
        self.iMergeRegions = 0
        self.iMergeMaterials = 0

        self._bodiesAndRegions = {}

        self.PhysVolToRegionMap = {}

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

    def makeRegionsDNF(self):
        for r in self.regionDict:
            self.regionDict[r] = self.regionDict[r].toDNF(r)

    def addLattice(self, lattice):
        if lattice.cellRegion.name in self.regionDict:
            msg = "LATTICE cell already been defined as a region in regionDict"
            raise ValueError(msg)
        self.latticeDict[lattice.cellRegion.name] = lattice

    def getBody(self, name):
        return self.bodyDict[name]

    def getBodyToRegionsMap(self):
        return self._bodiesAndRegions

    def printDefinitions(self):
        print(f"bodyDict = {self.bodyDict}")
        print(f"regionDict = {self.regionDict}")
        print(f"materialDict = {self.materials}")
        print(f"latticeDict = {self.latticeDict}")
        print(f"cardDict = {self.cardDict}")

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

    def addMaterial(self, material, recursive=False):
        name = material.name
        # Only allow redefinition of builtins..  anything else is
        # almost certainly not deliberate.
        if name in self.materials and name not in self._predefinedMaterialNames:
            raise _IdenticalNameError(name)
        self.materials[material.name] = material

        if recursive:
            if type(material) is Compound:
                for comp in material.fractions:
                    self.addMaterial(comp[0], True)

    def getMaterial(self, name):
        return self.materials[name]

    def addMaterialAssignments(self, mat, *regions, elc=None, mgn=None):
        if isinstance(mat, _Region):
            msg = "A Region instance has been provided as a material"
            raise TypeError(msg)

        try:  # Element or Compound instance
            materialName = mat.name
        except AttributeError:  # By name, get Ele/Comp from self.
            materialName = mat
            mat = self.materials[materialName]
        # More checks.
        if materialName not in self.materials:
            self.addMaterialAssignments(material)
        elif mat not in self.materials.values():
            msg = (
                f'Mismatch between provided FLUKA material "{mat.name}" for '
                "assignment and existing found in registry"
            )
            raise _FLUKAError(msg)

        for region in regions:
            # Either region name or Region instance
            try:
                name = region.name
            except AttributeError:
                name = region

            self.assignmas[name] = (materialName, elc, mgn)

    def assignma(self, material, *regions):
        return self.addMaterialAssignments(material, *regions)

    def addCard(self, card):
        if card.keyword in self.cardDict:
            self.cardDict[card.keyword].append(card)
        else:
            self.cardDict[card.keyword] = [card]

    def addTitle(self, title="FLUKA simulation"):
        c = _card.Card("TITLE", sdum="\n" + title)
        self.addCard(c)

    def addDefaults(self, default="EM-CASCA"):
        c = _card.Card("DEFAULTS", sdum=default)
        self.addCard(c)

    def addGlobal(self):
        pass

    def addBeam(
        self,
        energy,
        energySpread=0.1,
        beamDivergence=0,
        beamWidthX=0.1,
        beamWidthY=0.0,
        annular=-1,
        particleType="ELECTRON",
    ):
        c = _card.Card(
            "BEAM",
            energy,
            energySpread,
            beamDivergence,
            beamWidthX,
            beamWidthY,
            annular,
            particleType,
        )
        self.addCard(c)

    def addBeamPos(self, xpos=0, ypos=0, zpos=0, xdc=0, ydc=0):
        c = _card.Card("BEAMPOS", xpos, ypos, zpos, xdc, ydc)
        self.addCard(c)

    def addLowMat(self, flukaMat, lowENeutron1, lowENeutron2, lowENeutron3):
        # https://flukafiles.web.cern.ch/manual/chapters/low_energy_neutrons/multigroup_neutron_transport/neutron_cross_section_library/available_cross_sections.html
        c = _card.Card("LOW-MAT", flukaMat, lowENeutron1, lowENeutron2, lowENeutron3)
        self.addCard(c)

    def addLowMatAllMaterials(self):
        """
        Add LOWMAT card to all materials
        """
        mgXS = multiGroupNeutronCrossSections()

        for mat_name in self.materials:
            mat = self.materials[mat_name]
            if type(mat) is Material:
                ident = mgXS.findMaterial(round(mat.atomicNumber), round(mat.massNumber), 296)
                self.addLowMat(mat.name, ident[0], ident[1], ident[2])

    def addLowPwxs(self, what1=None, lowerMaterial=None, upperMaterial=None):
        if not what1:
            what1 = 0
        c = _card.Card("LOW-PWXS", what1=what1, what4=lowerMaterial, what5=upperMaterial)
        self.addCard(c)

    def addMgnCreat(self):
        pass

    def addMgnField(self):
        pass

    def addElcField(self):
        pass

    def addUsrBin(
        self,
        mesh=0,
        particle="ENERGY",
        lunOutput=-21,
        e1max=1,
        e2max=1,
        e3max=1,
        name="name",
        e1min=-1,
        e2min=-1,
        e3min=-1,
        e1nbin=10,
        e2nbin=10,
        e3nbin=10,
    ):
        c1 = _card.Card(
            "USRBIN",
            mesh,
            particle,
            lunOutput,
            e1max,
            e2max,
            e3max,
            name,
        )
        c2 = _card.Card("USRBIN", e1min, e2min, e3min, e1nbin, e2nbin, e3nbin, "&")

        self.addCard(c1)
        self.addCard(c2)

    def addRotprBin(self, precision=0, rotDefi=0, printEventBin=0, lowerBin=None, upperBin=None):
        if upperBin is None:
            upperBin = lowerBin

        c = _card.Card("ROTPRBIN", precision, rotDefi, printEvent, lowerBin, upperBin=None)

    def addUsrBdx(
        self,
        binning,
        scoringDir,
        scoringType,
        type,
        reg1,
        reg2,
        name,
        area=1.0,
        lunOutput=-22,
        maxKE=None,
        minKE=None,
        nKEbin=None,
        maxSA=None,
        minSA=None,
        nSAbin=None,
    ):
        c1 = _card.Card(
            "USRBDX",
            binning + 10 * scoringDir + 100 * scoringType,
            type,
            lunOutput,
            reg1,
            reg2,
            area,
            name,
        )
        c2 = _card.Card("USRBDX", maxKE, minKE, nKEbin, maxSA, minSA, nSAbin, "&")

        self.addCard(c1)
        self.addCard(c2)

    def addUsricall(self):
        c = _card.Card("USRICALL")
        self.addCard(c)

    def addUsrocall(self):
        c = _card.Card("USROCALL")
        self.addCard(c)

    def addUsrDump(self, mgdraw=100, lun=70, mgdrawOpt=-1, what4=0, sdum=None):
        if not sdum:
            c = _card.Card("USERDUMP", mgdraw, lun, mgdrawOpt, sdum=sdum)
            self.addCard(c)
        elif sdum == "UDQUENCH":
            c1 = _card.Card()

    def addRandomiz(self, seedLun=1, seed=54217137):
        c = _card.Card("RANDOMIZ", seedLun, seed)
        self.addCard(c)

    def addStart(
        self,
        maxPrimHistories=1,
        timeTermSec=None,
        coreDump=None,
        eachHistoryOutput=None,
    ):
        c = _card.Card("START", maxPrimHistories, None, timeTermSec, coreDump, eachHistoryOutput)
        self.addCard(c)

    def addPhotonuc(self, what1, mat_low, mat_high, mat_step, sdum=""):
        c = _card.Card(
            "PHOTONUC", what1=what1, what4=mat_low, what5=mat_high, what6=mat_step, sdum=sdum
        )
        self.addCard(c)

    def addMuphoton(self, what1, mat_low, mat_high, mat_step):
        c = _card.Card("MUPHOTON", what1=what1, what4=mat_low, what5=mat_high, what6=mat_step)
        self.addCard(c)

    def addPairbrem(self, what1, what2, what3, mat_low, mat_high, mat_step):
        c = _card.Card(
            "PAIRBREM",
            what1=what1,
            what2=what2,
            what3=what3,
            what4=mat_low,
            what5=mat_high,
            what6=mat_step,
        )
        self.addCard(c)

    def addDeltaRay(self, what1, what2, what3, mat_low, mat_high, mat_step, dsum="NOPRINT"):
        c = _card.Card(
            "DELTARAY",
            what1=what1,
            what2=what2,
            what3=what3,
            what4=mat_low,
            what5=mat_high,
            what6=mat_step,
            dsum=dsum,
        )
        self.addCard(c)

    def addIonFluct(self, what1, what2, what3, mat_low, mat_high, mat_step, dsum="PRIM-ION"):
        c = _card.Card(
            "IONFLUCT",
            what1=what1,
            what2=what2,
            what3=what3,
            what4=mat_low,
            what5=mat_high,
            what6=mat_step,
            dsum=dsum,
        )
        self.addCard(c)

    def printDumps(self, detail=1):
        if detail >= 1:
            print("regions", len(self.regionDict))
            if detail >= 2:
                for r in self.regionDict:
                    print("region", r, len(self.regionDict[r].zones), self.assignmas[r])
                    if detail >= 3:
                        print(self.regionDict[r].dumps())
                        print("")

    def findLastBodyIndex(self):
        """
        Find last body index (if the numbering was performed by a geant4 -> fluka conversion
        """

        maxIndex = -1
        for bodyKey in self.bodyDict.keys():
            if bodyKey == "BLKBODY":
                continue

            maxIndex = max(maxIndex, int(bodyKey[1:5]))

        return maxIndex

    def findLastRegionIndex(self):
        """
        Find last region index (if the numbering was performed by a geant4 -> fluka conversion
        """

        maxIndex = -1
        for regionKey in self.regionDict.keys():
            if regionKey == "BLKHOLE":
                continue

            maxIndex = max(maxIndex, int(regionKey[1:]))

        return maxIndex

    def findLastMaterialIndex(self):
        """
        Find last material index (if the numbering was performed by a geant4 -> fluka conversion
        """

        maxIndex = -1
        for materialKey in self.materials.keys():
            if materialKey == "BLCKHOLE" or materialKey.find("0") == -1:
                continue

            maxIndex = max(maxIndex, int(materialKey[1:4]))

        return maxIndex

    def findLastTransformationIndex(self):
        pass

    def checkBodyName(self, bodyName):
        if bodyName in self.bodyDict:
            return True, "C" + str(self.iMergeBodies)
        else:
            return False, bodyName

    def checkRegionName(self, regionName):
        if regionName in self.regionDict:
            return True, "S" + str(self.iMergeRegions)
        else:
            return False, regionName

    def checkMaterialName(self, materialName):
        if materialName in self.materials:
            return True, "N" + str(self.iMergeRegions)
        else:
            return False, materialName

    def addRegistry(
        self,
        flukaRegistry,
        outerRegion=None,
        rotation=[0, 0, 0],
        translation=[0, 0, 0],
        removeRegions=[],
        removeRegionDependents=False,
    ):
        def bodySetRename(body_set, old_name, new_name):
            for b in body_set:
                if b.name == old_name:
                    b.name = new_name

        # bodies (loop over solids)
        for body in flukaRegistry.bodyDict:
            # check body name
            old_body_name = body.name
            updated, new_body_name = self.checkBodyName(body.name)
            body.name = new_body_name

            print("body name replacement", old_body_name, new_body_name)

            # transform body
            mat4d = body.transform.to4DMatrix()
            mat4d_left = _np.lib.pad(_tbxyz2matrix(rotation), ((0, 1), (0, 1)))
            mat4d_left[:, 3] = [translation[0], translation[1], translation[2], 1]

            comp = mat4d_left @ mat4d
            compRotation = _matrix2tbxyz(comp[0:3, 0:3])
            compPosition = comp[3, 0:3]

            rotoTranslation = _rotoTranslationFromTra2(
                "BBROTDEF", [compRotation, compPosition], flukaregistry=flukaRegistry
            )
            body.transform = rotoTranslation

            # add body in self
            self.addBody(body)

            # if the name was updated change in the regions
            if updated:
                # update regions if body name has changed
                for regionKey in flukaRegistry.regionDict:
                    bodySetRename(
                        flukaRegistry.regionDict[regionKey].bodies(), old_body_name, new_body_name
                    )

            # update merged counter
            self.iMergeBodies += 1

        # regions (loop over regions) and also do assignmas at same time
        for regionKey in flukaRegistry.regionDict:
            region = flukaRegistry.regionDict[regionKey]

            # check body name
            old_region_name = region.name
            updated, new_region_name = self.checkRegionName(region.name)
            region.name = new_region_name

            print("region name replacement", old_region_name, new_region_name)

            # add body in self
            self.addRegion(region)

            # get material
            material = flukaRegistry.materials[flukaRegistry.assignmas[old_region_name]]

            updated, new_material_name = self.checkMaterialName(material.name)

            if updated and type(material) != BuiltIn:
                material.rename("N" + format(self.iMergeMaterials, "03"))
                self.iMergeMaterials += 1

            self.addMaterial(material, recursive=True)
            self.assignma(material.name, region.name)

            self.iMergeRegions += 1


class RotoTranslationStore(_MutableMapping):
    """only get by names."""

    def __init__(self):
        self._nameMap = _OrderedDict()
        # internal counter generating new unique transformation indices.
        self._counter = 2000

    def __getitem__(self, name):
        return self._nameMap[name]

    # def __repr__(self):
    #     return repr(self._nameMap).replace

    def __setitem__(self, name, rtrans):
        if not isinstance(rtrans, (_RotoTranslation, _RecursiveRotoTranslation)):
            msg = "Only store RotoTranslation or RecursiveRotoTranslation."
            raise TypeError(msg)
        if name != rtrans.name:
            msg = (
                "Name it is appended with doesn't match"
                " the name of the RotoTranslation instance..."
            )
            raise ValueError(msg)

        # If already defined then we give it the same transformation
        # index as the one we are overwriting.
        if name in self._nameMap:
            rtrans.transformationIndex = self._nameMap[name].transformationIndex
        self._nameMap[name] = rtrans

    def addRotoTranslation(self, rtrans):
        name = rtrans.name
        if name in self:  # match the name to the previous transformationIndex
            rtrans.transformationIndex = self[name].transformationIndex
            self[name].append(rtrans)
        else:
            # Insert as a RecursiveRotoTranslation to make any future
            # adding of RotoTranslations easier.
            recur = _RecursiveRotoTranslation(name, [rtrans])
            if not rtrans.transformationIndex:
                recur.transformationIndex = self._counter
                self._counter += 1000
            elif rtrans.transformationIndex in self.allTransformationIndices():
                msg = "transformation index matches another ROT-DEFI with a different name.  Change the transformationIndex and try again."
                raise KeyError(msg)
            elif rtrans.transformationIndex not in self.allTransformationIndices():
                pass  #
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

        self._cachers = {
            _body.XZP: hscacher,
            _body.YZP: hscacher,
            _body.XYP: hscacher,
            _body.PLA: hscacher,
            _body.XCC: infCylCacher,
            _body.YCC: infCylCacher,
            _body.ZCC: infCylCacher,
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
            del kwargs["flukaregistry"]  # Prevent infinite recursion
        except KeyError:
            pass
        try:
            result = self._cachers[clas].make(clas, *args, **kwargs)
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
            msg = f"Undefined body: {key}"
            raise _FLUKAError(msg)
        return self._df[self._df["name"] == key]["body"].item()

    def __delitem__(self, key):
        if key not in self._bodyNames():
            msg = f"Missing body name: {key}"
            raise KeyError(msg)

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
    COLUMNS = ["name", "body"]

    def __init__(self, df):
        self.df = df
        for column in self.COLUMNS:
            try:
                self.df.insert(len(self.df), column, [])
            except ValueError:  # already added the column maybe
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
            rowIndex = self.df[self.df["name"] == name].index
            msg = "operation not implemented"
            raise NotImplementedError(msg)

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
        if not mask.any():  # i.e. this half space has not been defined before.
            self.append(body)
            return body
        result = self.df[mask]["body"].item()
        return result  # self.df[mask]["body"].item()

    def getMask(self, columns, values, predicates):
        if self.df.empty:
            return _np.array([], dtype=bool)
        mask = _np.full_like(self.df["name"], True, dtype=bool)
        for column, value, predicate in zip(columns, values, predicates):
            mask &= self.df[column].apply(
                lambda x, value=value, predicate=predicate: predicate(x, _np.array(value)).all()
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
        return self.getMask(
            ["planeNormal", "pointOnPlane"], [normal, point], [_np.isclose, _np.isclose]
        )


class InfiniteCylinderCacher(Cacheable):
    COLUMNS = ["name", "body", "direction", "pointOnLine", "radius"]

    def append(self, body):
        super().appendData(
            [body.name, body, body.direction(), self._cylinderPoint(body), body.radius]
        )

    def mask(self, body):
        return self.getMask(
            ["direction", "pointOnLine", "radius"],
            [body.direction(), self._cylinderPoint(body), body.radius],
            [_vector.areParallelOrAntiParallel, _np.isclose, _np.isclose],
        )

    @staticmethod
    def _cylinderPoint(body):
        return _vector.pointOnLineClosestToPoint([0, 0, 0], body.point(), body.direction())


class FlukaBodyStoreExact:
    def __init__(self):
        self.nameBody = {}
        self.hashBody = {}
        self.hashName = {}

    def _bodyNames(self):
        return list(self.nameBody.keys())

    def _bodies(self):
        return list(self.nameBody.values())

    def make(self, cls, *args, **kwargs):
        body = cls(*args, **kwargs)
        return self.getDegenerateBody(body)

    def getDegenerateBody(self, body):
        if body.hash() in self.hashBody:
            return self.hashBody[body.hash()]
        else:
            self.addBody(body)
            return body

    def addBody(self, body):
        if body.name in self.nameBody:
            raise _IdenticalNameError(body.name)
        logger.debug("%s", body)

        self.nameBody[body.name] = body
        self.hashBody[body.hash()] = body
        self.hashName[body.hash()] = body.name

    def keys(self):
        return self._bodyNames()

    def values(self):
        return self.nameBody.values()

    def __setitem__(self, key, value):
        assert key == value.name
        self.addBody(value)
        # c = value.hash()
        # c.setBody(value)

    def __getitem__(self, key):
        if key not in self._bodyNames():
            msg = f"Undefined body: {key}"
            raise _FLUKAError(msg)
        return self.nameBody[key]

    def __delitem__(self, key):
        if key not in self._bodyNames():
            msg = f"Missing body name: {key}"
            raise KeyError(msg)

        body = self[key]
        b = self.nameBody.pop(key)
        self.hashBody.pop(b.hash())
        self.hashName.pop(b.hash())

    def __len__(self):
        return len(self.nameBody)

    def __contains__(self, key):
        return key in self._bodyNames()

    def __iter__(self):
        return iter(self._bodies())

    def __repr__(self):
        return repr(dict(zip(self._bodyNames(), self._bodies())))
