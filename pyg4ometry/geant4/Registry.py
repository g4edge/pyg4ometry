from collections import OrderedDict 

class Registry :
    def __init__(self) :
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

    def addDefinition(self, definition) :    
        self.definitionDict[definition.name] = definition

    def addMaterial(self, material) :
        self.materialDict[material.name] = material

    def addSolid(self,solid) :
        self.solidDict[solid.name] = solid

        try:
            self.solidTypeCountDict[solid.type] += 1
        except KeyError:
            self.solidTypeCountDict[solid.type] = 1

        try:
            self.solidUsageCountDict[solid.name] += 1
        except KeyError:
            self.solidUsageCountDict[solid.name] = 1

    def addLogicalVolume(self,volume) :
        self.logicalVolumeDict[volume.name] = volume       

        # total number of logical volumes
        try:
            self.volumeTypeCountDict["logicalVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["logicalVolume"] = 1
            
    def addPhysicalVolume(self,volume) : 
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


    def addReplicaVolume(self,volume) :
        self.replicaVolumeDict[volume.name] = volume
        
        try:
            self.volumeTypeCountDict["replicaVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["replicaVolume"] = 1

    def addParameterisedVolume(self,volume) :
        self.parametrisedVolumeDict[volume.name] = volume

        try :
            self.volumeTypeCountDict["parametrisedVolume"] += 1
        except KeyError:
            self.volumeTypeCountDict["parametrisedVolume"] = 1


    def addParameter(self, parameter):
        self.parameterDict[parameter.name] = parameter

    def setWorld(self, worldName) :
        self.worldName = worldName
        self.worldVolume = self.logicalVolumeDict[self.worldName]
        self.orderLogicalVolumes(worldName)
        self.logicalVolumeList.append(worldName)

    def orderLogicalVolumes(self, lvName) :
        '''Need to have a ordered list from most basic (solid) object upto physical/logical volumes for writing to
        GDML. GDML needs to have the solids/booleans/volumes defined in order'''

        lv = self.logicalVolumeDict[lvName]
        
        for daughters in lv.daughterVolumes : 
            dlvName = daughters.logicalVolume.name
            try : 
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

        if solid.type == 'union' or solid.type == 'intersecton' or solid.type == 'subtraction' :
            solidTree(solid.obj1.name)
            solidTree(solid.obj2.name)

    def clear(self) :
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

