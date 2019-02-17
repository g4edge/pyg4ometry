import pyg4ometry.exceptions
from   pyg4ometry.pycsg.geom import Vector as _Vector
from   pyg4ometry.pycsg.core import CSG    as _CSG

from   pyg4ometry.visualisation  import Mesh     as _Mesh
import solid                     as                 _solid
from   Material                  import Material as _Material
import pyg4ometry.transformation as                 _trans

import copy    as   _copy
import numpy   as   _np
import sys     as   _sys
import logging as   _log

class LogicalVolume(object):
    def __init__(self, solid, material, name, debug=False, registry=None, **kwargs):
        super(LogicalVolume, self).__init__()

        # geant4 required objects 
        self.solid           = solid

        if isinstance(material, _Material):
            self.material = material
        elif isinstance(material, str):
            self.material = _Material.nist(material)
        else:
            raise SystemExit("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []
        self.debug           = debug

        # geometry mesh
        self.mesh            = _Mesh(self.solid)

        # registry logic
        if registry:
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

            # scale 
            _log.info('LogicalVolume.checkOverlaps> scale %s' % (pv.name))
            mesh.scale(pv.scale.eval())

            # rotate 
            _log.info('LogicalVolume.checkOverlaps> rotate %s' % (pv.name))
            aa = _trans.tbxyz(pv.rotation.eval())
            mesh.rotate(aa[0],_trans.rad2deg(aa[1]))

            # translate 
            _log.info('LogicalVolume.checkOverlaps> translate %s'  % (pv.name))
            mesh.translate(pv.position.eval())
            
            transformedMeshes.append(mesh)

        # overlap daughter pv checks 
        for i in range(0,len(transformedMeshes)) : 
            for j in range(i+1,len(transformedMeshes)) :
                interMesh = transformedMeshes[i].intersect(transformedMeshes[j])
                self.mesh.addOverlapMesh(interMesh)
                _log.info('LogicalVolume.checkOverlaps> inter daughter %d %d %d %d' % (i,j, interMesh.vertexCount(), interMesh.polygonCount()))

        # overlap with solid 
        for i in range(0,len(transformedMeshes)) : 
            interMesh = transformedMeshes[i].intersect(self.mesh.localmesh.inverse())
            self.mesh.addOverlapMesh(interMesh)
            _log.info('LogicalVolume.checkOverlaps> daughter container %d %d %d' % (i, interMesh.vertexCount(), interMesh.polygonCount()))
                
    def extent(self) : 
        print 'LogicalVolume.extent> ', self.name

        for dv in self.daughterVolumes : 
            dv.extent()

