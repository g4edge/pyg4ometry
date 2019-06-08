import pyg4ometry.exceptions
from   pyg4ometry.pycsg.geom import Vector as _Vector
from   pyg4ometry.pycsg.core import CSG    as _CSG

from   pyg4ometry.visualisation  import Mesh     as _Mesh
import solid                     as                 _solid
import Material                  as                 _mat
import pyg4ometry.transformation as                 _trans

import copy    as   _copy
import numpy   as   _np
import sys     as   _sys
import logging as   _log

class LogicalVolume(object):
    '''
    LogicalVolume : G4LogicalVolume
    :param solid:  
    :param material:
    :param name: 
    :param registry:      
    :param addRegistry: 
    '''

    def __init__(self, solid, material, name, registry=None, addRegistry=True, **kwargs):
        super(LogicalVolume, self).__init__()

        # type 
        self.type            = "placement"
        
        # geant4 required objects 
        self.solid           = solid
 
        if isinstance(material, _mat.Material):
            self.material = material
        elif isinstance(material, str):
            # This will work out if it is a valid NIST and set the type appropriately
            self.material = _mat.MaterialPredefined(name=material)
        else:
            raise ValueError("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []

        # geometry mesh
        self.mesh            = _Mesh(self.solid)

        # registry logic
        if registry and addRegistry:
            registry.addLogicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Logical volume : '+self.name+' '+str(self.solid)+' '+str(self.material)

    def add(self, physicalVolume):
        self.daughterVolumes.append(physicalVolume)

    def checkOverlaps(self) :
        # local meshes 
        transformedMeshes = []

        # transform meshes into logical volume frame 
        for pv in self.daughterVolumes : 
            _log.info('LogicalVolume.checkOverlaps> %s' % (pv.name))
            mesh = pv.logicalVolume.mesh.localmesh.clone()

            # rotate 
            # _log.info('LogicalVolume.checkOverlaps> rotate %s' % (pv.name))
            aa = _trans.tbxyz2axisangle(pv.rotation.eval())
            mesh.rotate(aa[0],_trans.rad2deg(aa[1]))

            # translate 
            _log.info('LogicalVolume.checkOverlaps> translate %s'  % (pv.name))
            mesh.translate(pv.position.eval())
            
            transformedMeshes.append(mesh)

        # overlap daughter pv checks 
        for i in range(0,len(transformedMeshes)) : 
            for j in range(i+1,len(transformedMeshes)) :
                print self.daughterVolumes[i].name, self.daughterVolumes[j].name
                interMesh = transformedMeshes[i].intersect(transformedMeshes[j])
                self.mesh.addOverlapMesh(interMesh)
                _log.info('LogicalVolume.checkOverlaps> inter daughter %d %d %d %d' % (i,j, interMesh.vertexCount(), interMesh.polygonCount()))
                if interMesh.vertexCount() != 0  :
                    print "hello", self.daughterVolumes[i].name , self.daughterVolumes[j].name

        # overlap with solid 
        for i in range(0,len(transformedMeshes)) : 
            interMesh = transformedMeshes[i].intersect(self.mesh.localmesh.inverse())
            self.mesh.addOverlapMesh(interMesh)
            _log.info('LogicalVolume.checkOverlaps> daughter container %d %d %d' % (i, interMesh.vertexCount(), interMesh.polygonCount()))

            if interMesh.vertexCount() != 0 :
                print "hello", self.daughterVolumes[i].name, self.name

    def setSolid(self, solid) : 
        self.solid = solid 
        self.mesh  = _Mesh(self.solid)        
                
    def extent(self) : 
        _log.info('LogicalVolume.extent> %s ' % (self.name))
        
        [vMin, vMax] = self.mesh.getBoundingBox()

        # transform logical solid BB
                
        for dv in self.daughterVolumes : 
            [vMinDaughter, vMaxDaughter] = dv.extent()

            # transform daughter meshes to parent coordinates 
            dvmrot  = _trans.tbxyz2matrix(dv.rotation.eval())
            dvtra   = _np.array(dv.position.eval())            
            
            vMinDaughterParentCoords = _np.array((dvmrot.dot(vMinDaughter) + dvtra)[0,:])[0]
            vMaxDaughterParentCoords = _np.array((dvmrot.dot(vMaxDaughter) + dvtra)[0,:])[0]

            if vMaxDaughterParentCoords[0] > vMax[0] : 
                vMax[0] = vMaxDaughterParentCoords[0]
            if vMaxDaughterParentCoords[1] > vMax[1] : 
                vMax[1] = vMaxDaughterParentCoords[1] 
            if vMaxDaughterParentCoords[2] > vMax[2] : 
                vMax[2] = vMaxDaughterParentCoords[2] 

            if vMinDaughterParentCoords[0] < vMin[0] : 
                vMin[0] = vMinDaughterParentCoords[0]
            if vMinDaughterParentCoords[1] < vMin[1] : 
                vMin[1] = vMinDaughterParentCoords[1]
            if vMinDaughterParentCoords[2] < vMin[2] : 
                vMin[2] = vMinDaughterParentCoords[2] 


        return [vMin, vMax]

    def findLogicalByName(self,name) : 
        lv = [] 

        if self.name.find(name) != -1 : 
            lv.append(self)

        
        for d in self.daughterVolumes : 
            l = d.logicalVolume.findLogicalByName(name)
            if len(l) != 0 :
                lv.append(l)
        
        return lv
