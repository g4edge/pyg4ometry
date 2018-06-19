from collections import OrderedDict
import pyg4ometry.exceptions

class Registry:
    def __init__(self):
        self.defineDict                   = OrderedDict()
        self.materialDict                 = OrderedDict()
        self.solidDict                    = OrderedDict()
        self.logicalVolumeDict            = OrderedDict()
        self.physicalVolumeDict           = OrderedDict()
        self.replicaVolumeDict            = OrderedDict()
        self.parameterisedVolumeDict      = OrderedDict()
        self.parameterDict                = OrderedDict()
        self.logicalVolumeList            = []               # Ordered list of logical volumes from world down to bottom
        self.solidTypeCountDict           = {}               # Box, Cons etc
        self.solidUsageCountDict          = {}               # solidName1, solidName2
        self.volumeTypeCountDict          = {}               # logical, physical
        self.logicalVolumeUsageCountDict  = {}               # named logical usage in physical
        self.logicalVolumeMeshSkip        = []               # meshes to skip because they are inefficient

    def addDefinition(self, definition):
        try:
            self.defintionDict[definition.name]
            print 'definition replicated', defintion.name
            raise pyg4ometry.exceptions.IdenticalNameError(definition.name, "definition")
        except KeyError:
            self.definitionDict[definition.name] = definition


    def addMaterial(self, material):
        # try :
        #    self.materialDict[material.name]
        #    print 'material replicated', material.name
        #    raise pyg4ometry.exceptions.IdenticalNameError(
        #        material.name, "material")
        # except KeyError :
        self.materialDict[material.name] = material


    def addSolid(self,solid):
        try:
            self.solidDict[solid.name]
            print 'solid replicated', solid.name
            raise pyg4ometry.exceptions.IdenticalNameError(solid.name, "solid")
        except KeyError:
            self.solidDict[solid.name] = solid

        try:
            self.solidTypeCountDict[solid.type] += 1
        except KeyError:
            self.solidTypeCountDict[solid.type] = 1

        try:
            self.solidUsageCountDict[solid.name] += 1
        except KeyError:
            self.solidUsageCountDict[solid.name] = 1

    def addLogicalVolume(self,volume):
        try:
            self.logicalVolumeDict[volume.name]
            print 'logical replicated', volume.name
            raise pyg4ometry.exceptions.IdenticalNameError(volume.name,
                                                           "logical volume")
        except KeyError:
            self.logicalVolumeDict[volume.name] = volume

        # total number of logical volumes
        try:
            self.volumeTypeCountDict["logicalVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["logicalVolume"] = 1

    def addPhysicalVolume(self,volume):
        try:
            self.physicalVolumeDict[volume.name]
            print 'physical replicated', volume.name
            raise pyg4ometry.exceptions.IdenticalNameError(volume.name,
                                                           "physical volume")
        except KeyError:
            self.physicalVolumeDict[volume.name] = volume

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


    def addReplicaVolume(self,volume):
        self.replicaVolumeDict[volume.name] = volume

        try:
            self.volumeTypeCountDict["replicaVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["replicaVolume"] = 1

    def addParameterisedVolume(self,volume):

        try:
            self.parametrisedVolumeDict[volume.name]
            print 'parameterised replicated', volume.name
            raise pyg4ometry.exceptions.IdenticalNameError(
                volume.name, "parametrised volume")
        except KeyError:
            self.parametrisedVolumeDict[volume.name] = volume

        try:
            self.volumeTypeCountDict["parametrisedVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["parametrisedVolume"] = 1

    def addParameter(self, parameter):
        try:
            self.parameterDict[parameter.name]
            print 'parameter replicated', parameter.name
            raise pyg4ometry.exceptions.IdenticalNameError(parameter.name,
                                                           "parameter")
        except KeyError:
            self.parameterDict[parameter.name] = parameter


    def setWorld(self, worldName):
        self.worldName = worldName
        self.worldVolume = self.logicalVolumeDict[self.worldName]
        self.orderLogicalVolumes(worldName)
        self.logicalVolumeList.append(worldName)

    def orderLogicalVolumes(self, lvName):
        '''Need to have a ordered list from most basic (solid) object upto physical/logical volumes for writing to
        GDML. GDML needs to have the solids/booleans/volumes defined in order'''

        lv = self.logicalVolumeDict[lvName]
        
        print "mother> ",lv.name

        for daughters in lv.daughterVolumes:
            print "daughters> ",daughters.name

            dlvName = daughters.logicalVolume.name
            try:
                self.logicalVolumeList.index(dlvName)
            except ValueError:
                self.orderLogicalVolumes(dlvName)
                self.logicalVolumeList.append(dlvName)

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
        self.replicaVolumeDict.clear()
        self.parameterisedVolumeDict.clear()
        self.parameterDict.clear()

        self.logicalVolumeList = []
        self.solidTypeCountDict.clear()
        self.solidUsageCountDict.clear()
        self.logicalVolumeUsageCountDict.clear()
        self.logicalVolumeMeshSkip = []

registry = Registry()
