from collections import OrderedDict as _OrderedDict
import pyg4ometry.exceptions as _exceptions
from . import Material as _mat
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
    be used in conjunction with gdml Define objects for \
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

        self.solidUsageCountDict          = {}               # solidName1, solidName2
        self.volumeTypeCountDict          = {}               # logical, physical
        self.surfaceTypeCountDict         = {}               # border, skin
        self.logicalVolumeMeshSkip        = []               # meshes to skip because they are inefficient
        self.userInfo                     = []               # Ordered list for the user info, which is not processed

        self.solidNameCount               = {}
        self.materialNameCount            = {}
        self.logicalVolumeNameCount       = {}
        self.physicalVolumeNameCount      = {}
        self.surfaceNameCount             = {}
        self.defineNameCount              = {}

        self.solidTypeCountDict           = {}               # Box, Cons etc
        self.logicalVolumeUsageCountDict  = {}               # named logical usage in physical

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

    def addMaterial(self, material, namePolicy = "reuse"):
        """
        :param material: Material object for starage 
        :type material: Material
        """        

        if material.name in self.materialDict:
            if namePolicy == "none":
                if material.name.find("G4") != -1 :
                    return
                raise _exceptions.IdenticalNameError(material.name, "material")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                self.materialNameCount[material.name] += 1
                material.name = material.name + "_" + str(self.materialNameCount[material.name])
                self.materialDict[material.name] = material
        else :
            self.materialDict[material.name] = material
            self.materialNameCount[material.name] = 0

    def addSolid(self, solid, namePolicy="none"):
        """
        :param solid: Solid object for starage 
        :type solid: One of the geant4 solids
        """

        if solid.name in self.solidDict:
            if namePolicy == "none":
                raise _exceptions.IdenticalNameError(solid.name, "solid")
            elif namePolicy == "reuse":
                return
            elif namePolicy == "increment" :
                self.solidNameCount[solid.name] += 1
                solid.name = solid.name + "_"+str(self.solidNameCount[solid.name])
                self.solidDict[solid.name] = solid

        else :
            self.solidDict[solid.name] = solid
            self.solidNameCount[solid.name] = 0

        try:
            self.solidTypeCountDict[solid.type] += 1
        except KeyError:
            self.solidTypeCountDict[solid.type] = 0

    def addLogicalVolume(self,volume, namePolicy = "none"):
        """
        :param volume: LogicalVolume object for starage 
        :type volume: LogicalVolume
        """

        if volume.name in self.logicalVolumeDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(volume.name,"logical volume")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                self.logicalVolumeNameCount[volume.name] += 1
                volume.name = volume.name + "_" + str(self.logicalVolumeNameCount[volume.name])
                self.logicalVolumeDict[volume.name] = volume
        else :
            self.logicalVolumeDict[volume.name] = volume
            self.logicalVolumeNameCount[volume.name] = 0


        # total number of logical volumes
        try:
            self.volumeTypeCountDict["logicalVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["logicalVolume"] = 1

    def addPhysicalVolume(self,volume, namePolicy = "increment"):
        """
        :param volume: PhysicalVolume object for starage 
        :type volume: PhysicalVolume
        """

        if volume.name in self.physicalVolumeDict:
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(volume.name,"physical volume")
            elif namePolicy == "reuse" :
                return
            elif namePolicy == "increment" :
                self.physicalVolumeNameCount[volume.name] += 1
                volume.name = volume.name + "_" + str(self.physicalVolumeNameCount[volume.name])
                self.physicalVolumeDict[volume.name] = volume
        else :
            self.physicalVolumeDict[volume.name] = volume
            self.physicalVolumeNameCount[volume.name] = 0

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

    def addSurface(self, surface, namePolicy = "none"):
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
                self.surfaceNameCount[surface.name] += 1
                surface.name = "{}_{}".format(surface.name, self.surfaceNameCount[surface.name])
                self.surfaceDict[surface.name] = surface

        else :
            self.surfaceDict[surface.name] = surface
            self.surfaceNameCount[surface.name] = 0


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

    def addDefine(self, define, namePolicy = "none") :
        """
        :param define: Defintion object for starage 
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
                self.defineNameCount[define.name] += 1
                define.name = define.name + "_" + str(self.defineNameCount[define.name])
                self.defineDict[define.name] = define
        else :
            self.defineDict[define.name] = define
            self.defineNameCount[define.name] = 0

        return define.name

    def setWorld(self, worldName):
        self.worldName = worldName
        self.worldVolume = self.logicalVolumeDict[self.worldName]
        self.orderLogicalVolumes(worldName)
        self.logicalVolumeList.append(worldName)

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

        for name, obj in self.materialDict.items():  # Forces registered materials to
            if isinstance(obj, _mat.Material):           # recursively register their components too
                obj.set_registry(self)

        # Order is isotopes -> elements -> materials
        isotopes = []  # Isotopes and elements don't need internal ordering as no
        elements = []  # istotope of isotopes or element of elements
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

    def addVolumeRecursive(self, volume, namePolicy = "increment"):

        import pyg4ometry.geant4.LogicalVolume as _LogicalVolume
        import pyg4ometry.geant4.PhysicalVolume as _PhysicalVolume
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume


        self._registryOld = volume.registry

        if isinstance(volume, _PhysicalVolume) :

            # add its logical volume
            self.addVolumeRecursive(volume.logicalVolume, namePolicy = namePolicy)

            # add members from physical volume (NEED TO CHECK IF THE POSITION/ROTATION/SCALE DEFINE IS IN THE REGISTRY)
            self.transferDefines(volume.position,namePolicy)
            self.addDefine(volume.position,namePolicy)
            self.transferDefines(volume.rotation,namePolicy)
            self.addDefine(volume.rotation,namePolicy)
            if volume.scale :
                self.transferDefines(volume.scale, namePolicy)
                self.addDefine(volume.scale,namePolicy)
            self.addPhysicalVolume(volume,namePolicy)

        elif isinstance(volume, _LogicalVolume) :
            # loop over all daughters
            for dv in volume.daughterVolumes :
                self.addVolumeRecursive(dv, namePolicy)

            # add members from logical volume
            self.transferSolidDefines(volume.solid, namePolicy)
            self.addSolid(volume.solid,namePolicy)
            self.addMaterial(volume.material,"reuse")
            self.addLogicalVolume(volume,namePolicy)

        elif isinstance(volume, _AssemblyVolume) :
            # loop over all daughters
            for dv in volume.daughterVolumes :
                self.addVolumeRecursive(dv, namePolicy)

            # add members from logical volume
            self.addLogicalVolume(volume,namePolicy)


    def transferSolidDefines(self, solid, namePolicy):       # TODO make this work for all classes (using update variables method)

        if solid.type == "Subtraction" or solid.type == "Union" or solid.type == "Intersection" :
            self.transferSolidDefines(solid.obj1,namePolicy)
            self.transferSolidDefines(solid.obj2,namePolicy)
        elif solid.type == "MultiUnion" :
            for object in solid.objects :
                self.transferSolidDefines(object, namePolicy)

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
                self.transferDefines(v,namePolicy)

    def transferDefines(self, var, namePolicy):
        '''Transfer defines from one registry to another recursively'''

        import pyg4ometry.gdml.Defines as _Defines

        # If the variable is a position, rotation or scale
        if isinstance(var,_Defines.VectorBase) :
            for v in var.x.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy)

            for v in var.y.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy)

            for v in var.z.variables() :
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy)

            if var.name in self._registryOld.defineDict:
                var.name = self.addDefine(var,"reuse")
            var.setRegistry(self)
        # If a normal expression
        else :
            for v in var.expr.variables() :                       # loop over all variables needed for an express
                if v in self._registryOld.defineDict:      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy)

            if var.name in self._registryOld.defineDict:    # check if variable is stored in registry, if so need to be transferred
                var.name = self.addDefine(var, "reuse")           # probabably best to reuse here
            var.setRegistry(self)

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