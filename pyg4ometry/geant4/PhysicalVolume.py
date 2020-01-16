import pyg4ometry.transformation as _trans

from pyg4ometry.visualisation import VisualisationOptions as _VisOptions

import numpy as _np
import logging as _log

class PhysicalVolume(object):

    def __init__(self, rotation, position, logicalVolume, name,
                 motherVolume, registry=None, addRegistry = True, scale = None):
        '''
        PhysicalVolume : G4VPhysicalVolue, G4PVPlacement 
        :param rotation:  
        :param position:
        :param logicalVolume: pyg4ometry.geant4.LogicalVolume 
        :param name:      
        :param motherVolume: pyg4ometry.geant4.LogicalVolume
        :param registry: pyg4ometry.geant4.Registry
        :param addRegistry:
        '''
        
        super(PhysicalVolume, self).__init__()

        # type 
        self.type         = "placement"
    
        # need to determine type or rotation and position, as should be Position or Rotation type
        from pyg4ometry.gdml import Defines as _Defines

        if isinstance(position,list) :             
            position = _Defines.Position(name+"_pos",position[0],position[1],position[2],"mm",registry,False)
        if isinstance(rotation,list) :
            rotation = _Defines.Rotation(name+"_rot",rotation[0],rotation[1],rotation[2],"rad",registry,False)
        if isinstance(scale,list) :
            scale    = _Defines.Scale(name+"_sca",scale[0],scale[1],scale[2],"none",registry,False)


        # geant4 required objects
        self.rotation      = rotation
        self.position      = position
        self.scale         = scale
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

    def extent(self, includeBoundingSolid = True) :
        _log.info('PhysicalVolume.extent> %s' % (self.name))

        # transform daughter meshes to parent coordinates
        dvmrot = _trans.tbxyz2matrix(self.rotation.eval())
        dvtra = _np.array(self.position.eval())

        [vMin,vMax] = self.logicalVolume.extent(includeBoundingSolid)

        # TODO do we need scale here?
        vMinPrime = _np.array((dvmrot.dot(vMin) + dvtra)).flatten()
        vMaxPrime = _np.array((dvmrot.dot(vMax) + dvtra)).flatten()

        vmin = [min(a, b) for a, b in zip(vMinPrime, vMaxPrime)]
        vmax = [max(a, b) for a, b in zip(vMinPrime, vMaxPrime)]


        return [vmin, vmax]
