from pyg4ometry.visualisation import VisualisationOptions as _VisOptions

import copy    as _copy
import numpy   as _np
import sys     as _sys
import logging as _log


class PhysicalVolume(object):

    def __init__(self, rotation, position, logicalVolume, name,
                 motherVolume, registry=None, addRegistry = True):
        '''PhysicalVolume : G4PVPlacement 
        rotation      - 
        position      - 
        logicalVolume - pyg4ometry.geant4.LogicalVolume 
        name          - string 
        motherVolume  - pyg4ometry.geant4.LogicalVolume
        registry      - pyg4ometry.geant4.Registry
        addRegistry   - bool'''
        

        super(PhysicalVolume, self).__init__()
    
        # need to determine type or rotation and position, as should be Position or Rotation type
        from pyg4ometry.gdml import Defines as _Defines

        if isinstance(position,list) :             
            position = _Defines.Position(name+"_pos",position[0],position[1],position[2],"mm",registry,False)
        if isinstance(rotation,list) :
            rotation = _Defines.Rotation(name+"_rot",rotation[0],rotation[1],rotation[2],"rad",registry,False)

        # geant4 required objects
        self.rotation      = rotation
        self.position      = position
        self.logicalVolume = logicalVolume
        self.name          = name
        self.motherVolume  = motherVolume
        self.motherVolume.add(self)
        
        # physical visualisation options 
        self.visOptions    = _VisOptions()

        # registry logic
        if registry and addRegistry :
            registry.addPhysicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Physical Volume : '+self.name+' '+str(self.rotation)+' '+str(self.position)

    def extent(self) : 
        _log.info('PhysicalVolume.extent> %s' % (self.name))
        return self.logicalVolume.extent()
        
