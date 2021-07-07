import pyg4ometry.transformation as _trans
from   pyg4ometry.visualisation import OverlapType as _OverlapType

import logging as   _log

class AssemblyVolume(object) : 
    '''AssemblyVolume : similar to a logical volume but does not have a sense of 
    shape, material or field
    :param name: of assembly volume
    :type name:        
    :param registry: 
    :type registry: 
    :param addRegistry: 
    :type addRegistry: bool
    '''

    def __init__(self, name, registry=None, addRegistry=True) :
        super(AssemblyVolume, self).__init__()
        self.type            = "assembly"
        self.name            = name 
        self.daughterVolumes = []
        self.registry = registry
        if addRegistry :
            registry.addLogicalVolume(self)

        self.overlapChecked = False
            
    def __repr__(self):
        return 'Logical volume : '+self.name

    def add(self, physicalVolume) :
        self.daughterVolumes.append(physicalVolume)


    def extent(self, includeBoundingSolid=True) :
        _log.info('AssemblyVolume.extent> %s ' % (self.name))

        vMin = [1e99,1e99,1e99]
        vMax = [-1e99,-1e99,-1e99]

        for dv in self.daughterVolumes:
            [vMinDaughter, vMaxDaughter] = dv.extent()

            if vMaxDaughter[0] > vMax[0]:
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1]:
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2]:
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0]:
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1]:
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2]:
                vMin[2] = vMinDaughter[2]

        return [vMin, vMax]