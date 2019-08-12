import PhysicalVolume as _PhysicalVolume
from   pyg4ometry.visualisation  import Mesh as _Mesh
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
import pyg4ometry.transformation as _trans

import numpy as _np
import copy as _copy
import logging as _log

class ReplicaVolume(_PhysicalVolume.PhysicalVolume) : 
    '''
    ReplicaVolume: G4PVReplica

    :param name: of physical volume 
    :param logical: volume to be placed
    :param mother: logical volume, 
    :param axis: kXAxis,kYAxis,kZAxis,kRho,kPhi
    :param ncopies: number of replicas
    :param width: spacing between replicas along axis
    :param offset: of grid
    '''

    class Axis :
        kXAxis = 1
        kYAxis = 2
        kZAxis = 3
        kRho   = 4
        kPhi   = 5

    def __init__(self, name, logicalVolume, motherVolume, axis, nreplicas, 
                 width, offset = 0, registry = None, addRegistry=True, wunit = "", ounit= "") : 

        self.type                = "replica"        
        self.name                = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.axis                = axis

        self.nreplicas           = nreplicas
        self.width               = width
        self.offset              = offset
        self.wunit               = wunit
        self.ounit               = ounit

        self.visOptions          = _VisOptions()

        if addRegistry : 
            registry.addPhysicalVolume(self)

        # physical visualisation options
        self.visOptions    = _VisOptions()

        # Create replica meshes
        [self.meshes,self.transforms] = self.createReplicaMeshes()

    def createReplicaMeshes(self) :

        import pyg4ometry.gdml.Units as _Units

        nreplicas = int(self.nreplicas.eval())
        offset    = self.offset.eval()*_Units.unit(self.ounit)
        width     = self.width.eval()*_Units.unit(self.wunit)
        
        transforms = []
        meshes     = [] 

        for v,i in zip(_np.arange(-width*(nreplicas-1)*0.5,  width*(nreplicas+1)*0.5, width),range(0,nreplicas,1)) :
            if self.axis == self.Axis.kXAxis :
                rot = [0,0,0]
                trans = [v,0,0]
                transforms.append([rot,trans])
                meshes.append(self.logicalVolume.mesh)

                # if daughter contains a replica
                if len(self.logicalVolume.daughterVolumes) == 1 :
                    if isinstance(self.logicalVolume.daughterVolumes[0], ReplicaVolume) :
                        [daughter_meshes,daughter_transforms] = self.logicalVolume.daughterVolumes[0].createReplicaMeshes()
                        for m,t in zip(daughter_meshes,daughter_transforms) :
                            meshes.append(m)
                            transforms.append([rot,_np.array(trans)+_np.array(t[1])])

            elif self.axis == self.Axis.kYAxis :
                rot = [0,0,0]
                trans = [0,v,0]
                transforms.append([rot,trans])
                meshes.append(self.logicalVolume.mesh)

                # if daughter contains a replica
                if len(self.logicalVolume.daughterVolumes) == 1 :
                    if isinstance(self.logicalVolume.daughterVolumes[0], ReplicaVolume) :
                        [daughter_meshes,daughter_transforms] = self.logicalVolume.daughterVolumes[0].createReplicaMeshes()
                        for m,t in zip(daughter_meshes,daughter_transforms) :
                            meshes.append(m)
                            transforms.append([rot,_np.array(trans)+_np.array(t[1])])

            elif self.axis == self.Axis.kZAxis : 
                rot = [0,0,0]
                trans = [v,0,0]
                transforms.append([rot,trans])
                meshes.append(self.logicalVolume.mesh)

                # if daughter contains a replica
                if len(self.logicalVolume.daughterVolumes) == 1 :
                    if isinstance(self.logicalVolume.daughterVolumes[0], ReplicaVolume) :
                        [daughter_meshes,daughter_transforms] = self.logicalVolume.daughterVolumes[0].createReplicaMeshes()
                        for m,t in zip(daughter_meshes,daughter_transforms) :
                            meshes.append(m)
                            transforms.append([rot,_np.array(trans)+_np.array(t[1])])

        for v,i in zip(_np.arange(offset, offset+nreplicas*width,width),range(0,nreplicas,1)) :
            if self.axis == self.Axis.kRho :

                # Copy solid so we don't change the original
                solid       = _copy.deepcopy(self.logicalVolume.solid)
                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)
                # Must be a tubs 
                solid.pRMin.expr.expression = str(v)
                solid.pRMax.expr.expression = str(v+width)            
                mesh   = _Mesh(solid)                                

                meshes.append(mesh)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi : 
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,v],[0,0,0]])                
            
        return [meshes,transforms]

    def __repr__(self) :
        return 'Replica volume : '+self.name+' '+str(self.axis)+' '+str(self.nreplicas)+' '+str(self.offset)+' '+str(self.width)

    def extent(self, includeBoundingSolid = True):
        _log.info('ReplicaVolume.extent> %s' %(self.name))

        vMin = [1e99, 1e99, 1e99]
        vMax = [-1e99, -1e99, -1e99]

        for trans, mesh in zip(self.transforms, self.meshes) :
            # transform daughter meshes to parent coordinates
            dvmrot = _trans.tbxyz2matrix(trans[0])
            dvtra = _np.array(trans[1])

            [vMinDaughter, vMaxDaughter] = mesh.getBoundingBox()

            vMinDaughter = _np.array((dvmrot.dot(vMinDaughter) + dvtra)[0, :])[0]
            vMaxDaughter = _np.array((dvmrot.dot(vMaxDaughter) + dvtra)[0, :])[0]


            if vMaxDaughter[0] > vMax[0] :
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1] :
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2] :
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0] :
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1] :
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2] :
                vMin[2] = vMinDaughter[2]

        return [vMin,vMax]
