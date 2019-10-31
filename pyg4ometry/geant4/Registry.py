from collections import OrderedDict as _OrderedDict
import pyg4ometry.exceptions as _exceptions
import solid.SolidBase

def solidName(var) : 
    if isinstance(var,solid.SolidBase) :
        return var.name
    elif isinstance(var,str) :
        return var

class Registry:
    '''
    Object to store geometry for input and output. All of the pyg4ometry classes can be used without storing them in the Registry. The registry is used to write the GDML output file. A registry needs to be used in conjunction with gdml Define objects for evalation of expressions. 
    '''
    
    def __init__(self):
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

    def addMaterial(self, material, namePolicy = "none"):
        """
        :param material: Material object for starage 
        :type material: Material
        """        

        if self.materialDict.has_key(material.name) :
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

    def addSolid(self,solid, namePolicy = "none"):
        """
        :param solid: Solid object for starage 
        :type solid: One of the geant4 solids
        """

        if self.solidDict.has_key(solid.name) :
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(solid.name, "solid")
            elif namePolicy == "reuse" :
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

        if self.logicalVolumeDict.has_key(volume.name) :
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

        if self.physicalVolumeDict.has_key(volume.name) :
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

        if self.surfaceDict.has_key(surface.name) :
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
            print 'parameter replicated', parameter.name
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
        if _units.has_key(define.name):
            raise ValueError("Redefinition of a constant unit : {}".format(define.name))

        if self.defineDict.has_key(define.name):
            if namePolicy == "none" :
                raise _exceptions.IdenticalNameError(define.name,"define")
            elif namePolicy == "reuse" :
                return
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
            self.addVolumeRecursive(volume.logicalVolume)

            # add members from physical volume (NEED TO CHECK IF THE POSITION/ROTATION/SCALE DEFINE IS IN THE REGISTRY)
            self.addDefine(volume.position,namePolicy)
            self.addDefine(volume.rotation,namePolicy)
            if volume.scale :
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
        for varName in solid.varNames :

            # skip unit variables
            if varName.find("unit") != -1:
                continue
            # skip slicing variables
            if varName.find("slice") != -1:
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
                pass
            if isinstance(var,list) :                         # list of variables
                var = flatten(var)
            else :
                var = [var]                                   # single variable upgraded to list

            for v in var :                                    # loop over variables
                self.transferDefines(v,namePolicy)

                #if solid.registry.defineDict.has_key(v.name):# check if variable is stored in registry, if so need to be transferred
                #    v.name = self.addDefine(v,namePolicy)
                #v.setRegistry(self)

    def transferDefines(self, var, namePolicy):
        '''Transfer defines from one registry to another recursively'''

        import pyg4ometry.gdml.Defines as _Defines

        print var.name

        # If the variable is a position, rotation or scale
        if isinstance(var,_Defines.VectorBase) :
            if self._registryOld.defineDict.has_key(var.name):
                var.name = self.addDefine(var,"reuse")
            var.setRegistry(self)
        # If a normal expression
        else :
            print var.expr.variables()

            for v in var.expr.variables() :                       # loop over all variables needed for an express
                if self._registryOld.defineDict.has_key(v) :      # it in the other registry
                    self.transferDefines(self._registryOld.defineDict[v], namePolicy)

            if self._registryOld.defineDict.has_key(var.name):    # check if variable is stored in registry, if so need to be transferred
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
        print self.solidTypeCountDict
        print self.logicalVolumeUsageCountDict


registry = Registry()
