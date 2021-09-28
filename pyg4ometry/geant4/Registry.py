import pandas as _pd
from collections import OrderedDict as _OrderedDict
from collections import defaultdict as _defaultdict
import pyg4ometry.exceptions as _exceptions
from . import _Material as _mat
from . import solid


def solidName(var):
    if isinstance(var, solid.SolidBase):
        return var.name
    elif isinstance(var, str):
        return var


class Registry:
    """
    Object to store geometry for input and output. \
    All of the pyg4ometry classes can be used without \
    storing them in the Registry. The registry is used \
    to write the GDML output file. A registry needs to \
    be used in conjunction with GDML Define objects for \
    evaluation of expressions.
    """
    def __init__(self):
        self.materialList = []
        
        self.defineDict                   = _OrderedDict()
        self.materialDict                 = _OrderedDict()
        self.solidDict                    = _OrderedDict()
        self.logicalVolumeDict            = _OrderedDict()
        self.physicalVolumeDict           = _OrderedDict()
        self.physicalVolumeCountDict      = _OrderedDict()
        self.surfaceDict                  = _OrderedDict()
        self.loopDict                     = _OrderedDict()

        self.logicalVolumeList            = []               # Ordered list of logical volumes from world down to bottom

        self.solidUsageCountDict          = _defaultdict(int) # solidName1, solidName2
        self.volumeTypeCountDict          = _defaultdict(int) # logical, physical
        self.surfaceTypeCountDict         = _defaultdict(int) # border, skin
        self.logicalVolumeMeshSkip        = []                # meshes to skip because they are inefficient
        self.userInfo                     = []                # Ordered list for the user info, which is not processed
        
        self.defineNameCount              = _defaultdict(int)
        self.materialNameCount            = _defaultdict(int)
        self.solidNameCount               = _defaultdict(int)
        self.logicalVolumeNameCount       = _defaultdict(int)
        self.physicalVolumeNameCount      = _defaultdict(int)
        self.surfaceNameCount             = _defaultdict(int)


        self.solidTypeCountDict           = _defaultdict(int) # Box, Cons etc
        self.logicalVolumeUsageCountDict  = _defaultdict(int) # named logical usage in physical

        self.editedSolids                 = []               # Solids changed post-initialisation

        self.expressionParser = None

    def getExpressionParser(self):
        if not self.expressionParser:
            from pyg4ometry.gdml.Expression import ExpressionParser
            self.expressionParser = ExpressionParser()

        return self.expressionParser

    def registerSolidEdit(self, solid):
        if solid.name in self.solidDict:
            self.editedSolids.append(solid.name)

    def addMaterial(self, material):
        """
        :param material: Material object for storage
        :type material: Material
        """        

        if material.name in self.materialDict:
            if material.type == "nist":
                return
            raise _exceptions.IdenticalNameError(material.name, "material")
        else:
            self.materialDict[material.name] = material
            self.materialNameCount[material.name] = 0
            try:
                for component in material.components:
                    self.addMaterial(component[0])
            except AttributeError:
                # think this is a simple element need to check TODO
                pass

    def transferMaterial(self, material, incrementRenameDict={}):
        if material.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if material.name in self.materialDict:
            if material.type == "nist":
                return # nist ones generally aren't added and allowed to pass through
            else:
                self.materialNameCount[material.name] += 1
                newName = material.name + "_" + str(self.materialNameCount[material.name])
                incrementRenameDict[newName] = material.name
                material.name = newName
                for component in material.components:
                    self.transferMaterial(component[0], incrementRenameDict)
        else:
            incrementRenameDict[material.name] = material.name
            for component in material.components:
                self.transferMaterial(component[0], incrementRenameDict)

        self.materialDict[material.name] = material
        material.registry = self

    def addSolid(self, solid):
        """
        :param solid: Solid object for storage
        :type solid: One of the geant4 solids
        """

        if solid.name in self.solidDict:
            raise _exceptions.IdenticalNameError(solid.name, "solid")
        else:
            self.solidDict[solid.name] = solid

        self.solidTypeCountDict[solid.type] += 1
        self.solidNameCount[solid.name] += 1

    def transferSolid(self, solid, incrementRenameDict={}):
        """
        Transfer a solid into this registry instance. Updates
        the member solid.regsitry to be this registry.
        
        :param solid: Solid object for storage
        :type solid: One of the geant4 solids
        """
        if solid.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if solid.name in self.solidDict:
            # we already have a solid called this, so uniquely name it by incrementing it
            self.solidNameCount[solid.name] += 1
            newName = solid.name + "_" + str(self.solidNameCount[solid.name])
            incrementRenameDict[newName] = solid.name
            solid.name = newName
        else:
            incrementRenameDict[solid.name] = solid.name

        self.solidDict[solid.name] = solid
        solid.registry = self
            
        self.solidTypeCountDict[solid.type] += 1
        self.solidNameCount[solid.name] += 1

    def addLogicalVolume(self,volume, namePolicy="none", incrementRenameDict={}):
        """
        :param volume: LogicalVolume object for storage
        :type volume: LogicalVolume
        """

        if volume.name in self.logicalVolumeDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(volume.name,"logical volume")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                if volume.name in incrementRenameDict:
                    return
                self.logicalVolumeNameCount[volume.name] += 1
                newName =  volume.name + "_" + str(self.logicalVolumeNameCount[volume.name])
                incrementRenameDict[newName] = volume.name
                volume.name = newName
                self.logicalVolumeDict[volume.name] = volume
        else :
            self.logicalVolumeDict[volume.name] = volume
            self.logicalVolumeNameCount[volume.name] = 0
            incrementRenameDict[volume.name] = volume.name


        # total number of logical volumes
        try:
            self.volumeTypeCountDict["logicalVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["logicalVolume"] = 1

    def addPhysicalVolume(self,volume, namePolicy="increment", incrementRenameDict={}):
        """
        :param volume: PhysicalVolume object for storage
        :type volume: PhysicalVolume
        """

        if volume.name in self.physicalVolumeDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(volume.name,"physical volume")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                if volume.name in incrementRenameDict:
                    return
                self.physicalVolumeNameCount[volume.name] += 1
                newName = volume.name + "_" + str(self.physicalVolumeNameCount[volume.name])
                incrementRenameDict[newName] = volume.name
                volume.name = newName
                self.physicalVolumeDict[volume.name] = volume
        else :
            self.physicalVolumeDict[volume.name] = volume
            self.physicalVolumeNameCount[volume.name] = 0
            incrementRenameDict[volume.name] = volume.name

        # number of physical volumes
        try:
            self.volumeTypeCountDict["physicalVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["physicalVolume"] = 1

        # usage of logical volumes
        try:
            self.logicalVolumeUsageCountDict[volume.logicalVolume.name] += 1
        except KeyError:
            self.logicalVolumeUsageCountDict[volume.logicalVolume.name] = 1

    def addSurface(self, surface, namePolicy="none", incrementRenameDict={}):
        """
        :param surface: Surface
        :type surface:  pyg4ometry.geant4.BorderSurface or pyg4ometry.geant4.SkinSurface
        """

        if surface.name in self.surfaceDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(surface.name, "surface")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                if surface.name in incrementRenameDict:
                    return
                self.surfaceNameCount[surface.name] += 1
                newName = "{}_{}".format(surface.name, self.surfaceNameCount[surface.name])
                incrementRenameDict[newName] = surface.name
                surface.name = newName
                self.surfaceDict[surface.name] = surface

        else :
            self.surfaceDict[surface.name] = surface
            self.surfaceNameCount[surface.name] = 0
            incrementRenameDict[surface.name] = surface.name


        try:
            self.surfaceTypeCountDict[surface.type] += 1
        except KeyError:
            self.surfaceTypeCountDict[surface.type] = 0

    def addParameter(self, parameter):
        try:
            self.parameterDict[parameter.name]
            print(f'parameter replicated: {parameter.name}')
            raise _exceptions.IdenticalNameError(parameter.name,
                                                           "parameter")
        except KeyError:
            self.parameterDict[parameter.name] = parameter

    def addAuxiliary(self, auxiliary):
            self.userInfo.append(auxiliary)

    def addDefine(self, define, namePolicy="none", incrementRenameDict={}):
        """
        :param define: Definition object for storage
        :type define: Constant, Quantity, Variable, Matrix
        """

        from pyg4ometry.gdml.Units import units as _units
        if define.name in _units:
            raise ValueError("Redefinition of a constant unit : {}".format(define.name))

        if define.name in self.defineDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(define.name,"define")
            elif namePolicy == "reuse" :
                return define.name
            elif namePolicy == "increment" :
                if define.name in incrementRenameDict:
                    return define.name
                self.defineNameCount[define.name] += 1
                newName = define.name + "_" + str(self.defineNameCount[define.name])
                incrementRenameDict[newName] = newName
                define.name = newName
                self.defineDict[define.name] = define
        else :
            self.defineDict[define.name] = define
            self.defineNameCount[define.name] = 0
            incrementRenameDict[define.name] = define.name

        return define.name

    def transferDefines(self, var, namePolicy, incrementRenameDict={}):
        '''Transfer defines from one registry to another recursively'''

        import pyg4ometry.gdml.Defines as _Defines

        # If the variable is a position, rotation or scale
        if isinstance(var,_Defines.VectorBase) :
            for v in var.x.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy, incrementRenameDict)

            for v in var.y.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy, incrementRenameDict)

            for v in var.z.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy, incrementRenameDict)

            if var.name in self._registryOld.defineDict:
                var.name = self.addDefine(var, namePolicy, incrementRenameDict)
            var.setRegistry(self)
        # If a normal expression
        else :
            for v in var.expr.variables() :                # loop over all variables needed for an express
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy, incrementRenameDict)

            if var.name in self._registryOld.defineDict:                        # check if variable is stored in registry, if so need to be transferred
                var.name = self.addDefine(var, namePolicy, incrementRenameDict) # probably best to reuse here
            var.setRegistry(self)

    def setWorld(self, worldIn):
        """
        The argument can either be the name of logical volume of the world
        or the pyg4ometry.geant4.LogicalVolume instance of the world volume.
        The term world is used to refer to the outermost volume of the hierarchy.
        """
        if type(worldIn) is str:
            # assume it's the name of the world volume
            self.worldName = worldIn
            self.worldVolume = self.logicalVolumeDict[worldIn]
            self.orderLogicalVolumes(worldIn)
            self.logicalVolumeList.append(worldIn)
        else:
            self.worldName = worldIn.name
            self.worldVolume = worldIn
            if worldIn not in self.logicalVolumeDict:
                self.logicalVolumeDict[worldIn.name] = worldIn
            self.logicalVolumeList.append(worldIn.name)

    def _orderMaterialList(self, materials, materials_ordered=[]):
        for mat in materials:
            if isinstance(mat, _mat.Material) and mat not in materials_ordered:
                component_objects = [comp[0] for comp in mat.components]
                materials_ordered = self._orderMaterialList(component_objects, materials_ordered)
                materials_ordered.append(mat)
        return materials_ordered

    def orderMaterials(self):
        '''Need to have a ordered list of all material entities for writing to
        GDML. GDML needs to have the isotopes/elements/materials defined in use order'''

        for name in list(self.materialDict.keys()):  # Forces registered materials to
            if isinstance(self.materialDict[name], _mat.Material):           # recursively register their components too
                self.materialDict[name].set_registry(self)

        # Order is isotopes -> elements -> materials
        isotopes = []  # Isotopes and elements don't need internal ordering as no
        elements = []  # isotope of isotopes or element of elements
        materials = []  # Material do need internal ordering as material of materials is possible
        for name, obj in self.materialDict.items():
            if isinstance(obj, _mat.Isotope):
                isotopes.append(obj)
            elif isinstance(obj, _mat.Element):
                elements.append(obj)
            else:
                materials.append(obj)

        materials_ordered = self._orderMaterialList(materials)
        self.materialList = isotopes + elements + materials_ordered

    def orderLogicalVolumes(self, lvName, first = True):
        '''Need to have a ordered list from most basic (solid) object upto physical/logical volumes for writing to
        GDML. GDML needs to have the solids/booleans/volumes defined in order'''

        if first :
            self.logicalVolumeList = []

        lv = self.logicalVolumeDict[lvName]
        
        # print "mother> ",lv.name
        for daughters in lv.daughterVolumes:
            # print "daughters> ",daughters.name

            dlvName = daughters.logicalVolume.name
            try:
                self.logicalVolumeList.index(dlvName)
            except ValueError:
                self.orderLogicalVolumes(dlvName,False)
                self.logicalVolumeList.append(dlvName)

    def addVolumeRecursive(self, volume, namePolicy="increment", incrementRenameDict=None):
        if incrementRenameDict is None:
            incrementRenameDict = {}
        import pyg4ometry.geant4.LogicalVolume as _LogicalVolume
        import pyg4ometry.geant4.PhysicalVolume as _PhysicalVolume
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume

        self._registryOld = volume.registry

        if isinstance(volume, _PhysicalVolume) :

            # add its logical volume
            self.addVolumeRecursive(volume.logicalVolume, namePolicy, incrementRenameDict)

            # add members from physical volume (NEED TO CHECK IF THE POSITION/ROTATION/SCALE DEFINE IS IN THE REGISTRY)
            self.transferDefines(volume.position ,namePolicy, incrementRenameDict)
            self.addDefine(volume.position, namePolicy, incrementRenameDict)
            self.transferDefines(volume.rotation, namePolicy, incrementRenameDict)
            self.addDefine(volume.rotation, namePolicy, incrementRenameDict)
            if volume.scale:
                self.transferDefines(volume.scale, namePolicy, incrementRenameDict)
                self.addDefine(volume.scale, namePolicy, incrementRenameDict)
            self.addPhysicalVolume(volume, namePolicy, incrementRenameDict)

        elif isinstance(volume, _LogicalVolume) :
            # loop over all daughters
            for dv in volume.daughterVolumes :
                self.addVolumeRecursive(dv, namePolicy, incrementRenameDict)

            # add members from logical volume
            self.transferSolidDefines(volume.solid, namePolicy, incrementRenameDict)
            self.addSolid(volume.solid, namePolicy, incrementRenameDict)
            self.addMaterial(volume.material, namePolicy, incrementRenameDict)
            self.addLogicalVolume(volume,namePolicy, incrementRenameDict)

        elif isinstance(volume, _AssemblyVolume) :
            # loop over all daughters
            for dv in volume.daughterVolumes :
                self.addVolumeRecursive(dv, namePolicy, incrementRenameDict)

            # add members from logical volume
            self.addLogicalVolume(volume, namePolicy, incrementRenameDict)
        else :
            print("Volume type not supported yet for merging")

        return incrementRenameDict

    def transferSolidDefines(self, solid, namePolicy, incrementRenameDict={}):       # TODO make this work for all classes (using update variables method)

        if solid.type == "Subtraction" or solid.type == "Union" or solid.type == "Intersection" :
            self.transferSolidDefines(solid.obj1,namePolicy,incrementRenameDict)
            self.transferSolidDefines(solid.obj2,namePolicy,incrementRenameDict)
        elif solid.type == "MultiUnion" :
            for object in solid.objects :
                self.transferSolidDefines(object, namePolicy, incrementRenameDict)

        for varName in solid.varNames :

            # skip unit variables
            if varName.find("unit") != -1:
                continue
            # skip slicing variables
            if varName.find("slice") != -1 and varName.find("pZslices") == -1 :
                continue
            # skip stack variables
            if varName.find("stack") != -1:
                continue


            def flatten(S):
                if S == []:
                    return S
                if isinstance(S[0], list):
                    return flatten(S[0]) + flatten(S[1:])
                return S[:1] + flatten(S[1:])

            var = getattr(solid,varName)

            if isinstance(var,int) :                          # int could not be in registry
                continue
            if isinstance(var,float) :                        # float  could not be in registry
                continue
            if isinstance(var,str) :                          # could be an expression
                continue
            if isinstance(var,list) :                         # list of variables
                var = flatten(var)
            else :
                var = [var]                                   # single variable upgraded to list

            for v in var :                                    # loop over variables
                self.transferDefines(v,namePolicy,incrementRenameDict)

    def volumeTree(self, lvName):
        '''Not sure what this method is used for'''
        lv = self.logicalVolumeDict[lvName]

    def solidTree(self, solidName):
        '''Not sure what this method is used for'''
        solid = self.solidDict[solidName]

        if solid.type == 'union' or solid.type == 'intersecton' or solid.type == 'subtraction':
            solidTree(solid.obj1.name)
            solidTree(solid.obj2.name)

    def clear(self):
        '''Empty all internal structures'''
        self.defineDict.clear()
        self.materialDict.clear()
        self.solidDict.clear()
        self.volumeTypeCountDict.clear()
        self.logicalVolumeDict.clear()
        self.physicalVolumeDict.clear()

        self.logicalVolumeList = []
        self.solidTypeCountDict.clear()
        self.solidUsageCountDict.clear()
        self.logicalVolumeUsageCountDict.clear()
        self.logicalVolumeMeshSkip = []

    def getWorldVolume(self) :         
        return self.worldVolume

    def printStats(self):
        print(self.solidTypeCountDict)
        print(self.logicalVolumeUsageCountDict)

    def toFlukaRegistry(self):
        import pyg4ometry.fluka as _f

        freg = _f.FlukaRegistry()

    def structureAnalysis(self, lv_name=None, debug=False, level=0, df=None):

        if lv_name is None:
            lv_name = self.getWorldVolume().name

        if df is None:
            self.logicalVolumeList = []
            df = _pd.DataFrame(columns=['level', 'mother', 'material', 'daughters', 'mother_lv', 'daughters_lv'])

        mother_lv = self.logicalVolumeDict[lv_name]
        mother = mother_lv.name
        daughters_lv = [daughter.logicalVolume for daughter in mother_lv.daughterVolumes]
        daughters = [daughter.name for daughter in daughters_lv]
        material = mother_lv.material.name.split('0')[0]

        df = df.append({'level': level, 'mother_lv': mother_lv, 'mother': mother, 'daughters_lv': daughters_lv,
                        'daughters': daughters, 'material': material}, ignore_index=True)

        if debug:
            print("\nlevel:", level)
            print("mother:", mother)
            print("daughters: ", len(daughters), " ", daughters)

        level += 1

        for daughters in mother_lv.daughterVolumes:
            lv_name = daughters.logicalVolume.name
            try:
                self.logicalVolumeList.index(lv_name)
            except ValueError:
                df = self.structureAnalysis(lv_name, debug, level, df)
                self.logicalVolumeList.append(lv_name)

        return df


class GeometryComplexityInformation:
    def __init__(self):
        self.solids            = _defaultdict(int)
        self.nDaughtersPerLV   = _defaultdict(int)
        self.nDaughters        = {}
        self.booleanDepthCount = _defaultdict(int)
        self.booleanDepth      = _defaultdict(int)

    def printSummary(self, boolDepthLimit=3):
        print("Types of solids")
        solidsSorted = sorted(self.solids.items(),key=lambda x: x[1], reverse=True)
        for solidName,number in solidsSorted:
            print(solidName.ljust(20),':',number)
        
        print(" ")
        print("# of daughters".ljust(20),"count")
        for nDaughters in sorted(self.nDaughtersPerLV.keys()):
            print(str(nDaughters).ljust(20), ':', self.nDaughtersPerLV[nDaughters])

        print(" ")
        print("Depth of booleans".ljust(20),"count")
        for boolDepth in sorted(self.booleanDepthCount.keys()):
            print(str(boolDepth).ljust(20), ':', self.booleanDepthCount[boolDepth])

        print(" ")
        print("Booleans width depth over ",boolDepthLimit)
        print("Solid name".ljust(40),":","n Booleans")
        boolDepthSorted = sorted(self.booleanDepth.items(),key=lambda x: x[1], reverse=True)
        for solidName,boolDepth in boolDepthSorted:
            if boolDepth > boolDepthLimit:
                print(solidName.ljust(40),":",boolDepth)
        

def AnalyseGeometryComplexity(logicalVolume):
    """
    Analyse a geometry tree starting from a logical volume.
    Produces an instance of :class:`GeometryComplexityInformation` with
    summary information. Provides:
    
    * count per solid type
    * number of daughters per logical volume
    * dictionary of N daughters for each logical volume name
    * depth count of Boolean solids

    ie a Boolean of a Boolean returns 2, a Boolean of two primitives returns 1

    * a dictionary of boolean depth for each logical volume name

    Example: ::

        info = AnalyseGeometryComplexity(lv)
        info.printSummary()
    """
    result = GeometryComplexityInformation()
    result = _UpdateComplexity(logicalVolume, result)
    return result

def _UpdateComplexity(lv, info):
    if lv.type != "assembly" :
        info.solids[lv.solid.type] += 1

    info.nDaughters[lv.name] = len(lv.daughterVolumes)
    info.nDaughtersPerLV[len(lv.daughterVolumes)] +=1

    booleanTypes = ['Union', 'Subtraction', 'Intersection']
    
    def _CountDaughterBooleanSolids(solid, number=0):
        for solid in [solid.obj1, solid.obj2]:
            if solid.type in booleanTypes:
                number += 1
                number = _CountDaughterBooleanSolids(solid, number)
        return number           

    if lv.type != "assembly" and lv.solid.type in booleanTypes:
        nBooleans = 1
        nBooleans = _CountDaughterBooleanSolids(lv.solid, nBooleans)
        info.booleanDepthCount[nBooleans] += 1
        info.booleanDepth[lv.name] = nBooleans

    # recurse
    for pv in lv.daughterVolumes:
        info = _UpdateComplexity(pv.logicalVolume, info)
    
    return info
