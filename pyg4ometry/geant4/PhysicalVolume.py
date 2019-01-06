import copy as _copy
import numpy as _np

from pyg4ometry.transformation import *
from pyg4ometry.visualisation import Mesh as _Mesh

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

        # required for visualisation of the physical volume
        self.mesh          = _Mesh(self.logicalVolume.solid)

        if registry:
            registry.addPhysicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Physical Volume : '+self.name+' '+str(self.rotation)+' '+str(self.position)

    def updateSceneTree(self, rot, tra) :
        print 'PhysicalVolume.updateSceneTree>',self.name+'\n', rot, tra

        # compute the updated transformation for this physical volume to the world
        # rot*(self.rot*v+self.tra) + tra
        # rot*self.rot *v + rot*self.tra + tra                     
        
        selfmrot  = tbxyz2matrix(self.rotation.eval())
        selftra   = _np.array(self.position.eval())

        new_mrot = rot*selfmrot
        new_tra  = rot.dot(selftra) + tra

        rot = new_mrot 
        tra = new_tra

        self.logicalVolume.updateSceneTree(rot,tra)
        self.mesh.transformLocalMesh(rot,tra)

        # if logical volume has daughers set to wireframe or transparent  
        if len(self.logicalVolume.daughterVolumes) != 0 :
            self.mesh.wireframe = True

    def extent(self) : 
        print 'PhysicalVolume.extent> ', self.name
        self.logicalVolume.extent()
        
