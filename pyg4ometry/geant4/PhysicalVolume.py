import copy as _copy
import numpy as _np

from pyg4ometry.transformation import *

import sys as _sys

class PhysicalVolume(object):
    '''Geant4 Physical volume class'''

    def __init__(self, rotation, position, logicalVolume, name,
                 motherVolume, scale=[1,1,1], debug=False, registry=None):
        super(PhysicalVolume, self).__init__()

        # need to determine type or rotation and position, as should be Position or Rotation type

        self.rotation      = rotation
        self.position      = position
        self.logicalVolume = logicalVolume
        self.name          = name
        self.motherVolume  = motherVolume
        self.motherVolume.add(self)
        self.scale         = scale
        self.debug         = debug

        if registry:
            registry.addPhysicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Physical Volume : '+self.name+' '+str(self.rotation)+' '+str(self.position)

    def extent(self) : 
        print 'PhysicalVolume.extent> ', self.name
        self.logicalVolume.extent()
        
